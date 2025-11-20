"""
WebSocket Real-Time Server
===========================

Provides real-time updates for:
- Activity logging notifications
- Performance score updates
- Live leaderboards
- Team notifications
"""

from typing import Dict, Set, List, Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi import APIRouter
import json
import asyncio
from datetime import datetime
import redis.asyncio as redis


router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    Supports:
    - User-specific connections
    - Room-based broadcasting
    - Redis pub/sub for horizontal scaling
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize connection manager.

        Args:
            redis_url: Redis URL for pub/sub (optional, for scaling)
        """
        # Active connections: {user_id: [websockets]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # Room subscriptions: {room_name: {user_id}}
        self.rooms: Dict[str, Set[str]] = {}

        # Redis for scaling across multiple servers
        self.redis_url = redis_url
        self.redis_client = None
        self.redis_pubsub = None

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept WebSocket connection and register user.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Disconnect WebSocket and clean up.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from all rooms
        for room in self.rooms.values():
            room.discard(user_id)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific WebSocket.

        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        await websocket.send_json(message)

    async def broadcast_to_user(self, message: dict, user_id: str):
        """
        Broadcast message to all connections for a user.

        Args:
            message: Message dictionary
            user_id: Target user ID
        """
        if user_id in self.active_connections:
            disconnected = set()

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    disconnected.add(connection)

            # Clean up disconnected sockets
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)

    async def broadcast_to_room(self, message: dict, room: str):
        """
        Broadcast message to all users in a room.

        Args:
            message: Message dictionary
            room: Room name
        """
        if room in self.rooms:
            for user_id in self.rooms[room]:
                await self.broadcast_to_user(message, user_id)

    async def join_room(self, user_id: str, room: str):
        """
        Add user to a room.

        Args:
            user_id: User ID
            room: Room name
        """
        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(user_id)

    async def leave_room(self, user_id: str, room: str):
        """
        Remove user from a room.

        Args:
            user_id: User ID
            room: Room name
        """
        if room in self.rooms:
            self.rooms[room].discard(user_id)

    async def setup_redis(self):
        """Setup Redis pub/sub for multi-server scaling."""
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_pubsub = self.redis_client.pubsub()

            # Subscribe to channels
            await self.redis_pubsub.subscribe("healthrix:activities", "healthrix:performance")

            # Start listening task
            asyncio.create_task(self._redis_listener())

    async def _redis_listener(self):
        """Listen for Redis pub/sub messages and broadcast."""
        async for message in self.redis_pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                channel = message["channel"].decode()

                if channel == "healthrix:activities":
                    await self.handle_activity_event(data)
                elif channel == "healthrix:performance":
                    await self.handle_performance_event(data)

    async def publish_redis(self, channel: str, message: dict):
        """
        Publish message to Redis channel.

        Args:
            channel: Redis channel name
            message: Message dictionary
        """
        if self.redis_client:
            await self.redis_client.publish(channel, json.dumps(message))

    async def handle_activity_event(self, data: dict):
        """Handle activity event from Redis."""
        # Broadcast to relevant users/rooms
        emp_id = data.get("emp_id")
        if emp_id:
            await self.broadcast_to_user({
                "type": "activity",
                "event": "new",
                "data": data
            }, emp_id)

        # Also broadcast to team room
        await self.broadcast_to_room({
            "type": "activity",
            "event": "new",
            "data": data
        }, "team")

    async def handle_performance_event(self, data: dict):
        """Handle performance event from Redis."""
        emp_id = data.get("emp_id")
        if emp_id:
            await self.broadcast_to_user({
                "type": "performance",
                "event": "updated",
                "data": data
            }, emp_id)


# Global connection manager
manager = ConnectionManager()


# WebSocket Endpoints

@router.websocket("/ws/activities")
async def websocket_activities(
    websocket: WebSocket,
    token: str,  # JWT token for authentication
):
    """
    WebSocket endpoint for activity updates.

    Streams real-time activity notifications.
    """
    # TODO: Validate JWT token and get user_id
    user_id = "user123"  # Extract from token

    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle client messages
            message_type = data.get("type")

            if message_type == "subscribe":
                # Subscribe to specific activity types or users
                filter_type = data.get("filter")
                if filter_type == "team":
                    await manager.join_room(user_id, "team")
                    await manager.send_personal_message({
                        "type": "subscription",
                        "status": "subscribed",
                        "room": "team"
                    }, websocket)

            elif message_type == "ping":
                # Keepalive
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/performance")
async def websocket_performance(
    websocket: WebSocket,
    token: str,
):
    """
    WebSocket endpoint for performance updates.

    Streams real-time performance score updates.
    """
    # TODO: Validate JWT token
    user_id = "user123"

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "subscribe_leaderboard":
                await manager.join_room(user_id, "leaderboard")

                # Send initial leaderboard
                # TODO: Fetch from database
                await manager.send_personal_message({
                    "type": "leaderboard",
                    "data": []
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/leaderboard")
async def websocket_leaderboard(
    websocket: WebSocket,
    token: str,
):
    """
    WebSocket endpoint for live leaderboard.

    Streams real-time leaderboard updates.
    """
    user_id = "user123"  # From token

    await manager.connect(websocket, user_id)
    await manager.join_room(user_id, "leaderboard")

    try:
        # Send leaderboard updates every 30 seconds
        while True:
            # TODO: Fetch current leaderboard from database
            leaderboard_data = {
                "type": "leaderboard",
                "timestamp": datetime.utcnow().isoformat(),
                "data": []
            }

            await manager.send_personal_message(leaderboard_data, websocket)

            # Wait 30 seconds before next update
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        await manager.leave_room(user_id, "leaderboard")


# Helper functions to trigger events from API

async def notify_activity_logged(activity_data: dict):
    """
    Notify connected clients about new activity.

    Args:
        activity_data: Activity information
    """
    # Broadcast to WebSocket clients
    emp_id = activity_data.get("emp_id")
    if emp_id:
        await manager.broadcast_to_user({
            "type": "activity",
            "event": "logged",
            "data": activity_data,
            "timestamp": datetime.utcnow().isoformat()
        }, emp_id)

    # Publish to Redis for other servers
    await manager.publish_redis("healthrix:activities", activity_data)


async def notify_performance_calculated(performance_data: dict):
    """
    Notify connected clients about performance calculation.

    Args:
        performance_data: Performance score information
    """
    emp_id = performance_data.get("emp_id")
    if emp_id:
        await manager.broadcast_to_user({
            "type": "performance",
            "event": "calculated",
            "data": performance_data,
            "timestamp": datetime.utcnow().isoformat()
        }, emp_id)

    # Publish to Redis
    await manager.publish_redis("healthrix:performance", performance_data)


async def update_leaderboard(leaderboard_data: List[dict]):
    """
    Update leaderboard for all subscribers.

    Args:
        leaderboard_data: Current leaderboard
    """
    await manager.broadcast_to_room({
        "type": "leaderboard",
        "event": "updated",
        "data": leaderboard_data,
        "timestamp": datetime.utcnow().isoformat()
    }, "leaderboard")


# Example usage in API endpoints
"""
# In your activities endpoint:

@app.post("/api/v1/activities")
async def create_activity(activity: ActivityCreate):
    # ... create activity in database ...

    # Notify WebSocket clients
    await notify_activity_logged({
        "emp_id": activity.emp_id,
        "task_name": activity.task_name,
        "count": activity.count,
        "date": activity.date.isoformat()
    })

    return activity


# In your performance calculation endpoint:

@app.post("/api/v1/performance/calculate")
async def calculate_performance(date: str):
    # ... calculate performance ...

    for score in scores:
        # Notify WebSocket clients
        await notify_performance_calculated({
            "emp_id": score.emp_id,
            "date": score.date.isoformat(),
            "final_performance": score.final_performance_percent
        })

    return scores


# Initialize Redis on startup:

@app.on_event("startup")
async def startup_event():
    await manager.setup_redis()
"""
