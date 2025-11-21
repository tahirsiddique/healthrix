"""
Prometheus Metrics Exporter
============================

Exposes application metrics for Prometheus monitoring.

Metrics tracked:
- API request rates and latencies
- Database query performance
- Performance calculations
- User activity
- System health
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
from functools import wraps
import time
from typing import Callable


# Create custom registry
registry = CollectorRegistry()

# API Metrics
http_requests_total = Counter(
    'healthrix_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'healthrix_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=registry
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'healthrix_db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table'],
    registry=registry
)

db_connections_active = Gauge(
    'healthrix_db_connections_active',
    'Active database connections',
    registry=registry
)

# Business Metrics
activities_logged_total = Counter(
    'healthrix_activities_logged_total',
    'Total activities logged',
    ['task_type'],
    registry=registry
)

performance_calculations_total = Counter(
    'healthrix_performance_calculations_total',
    'Total performance calculations',
    ['type'],  # individual, team, all
    registry=registry
)

performance_calculation_duration_seconds = Summary(
    'healthrix_performance_calculation_duration_seconds',
    'Performance calculation duration',
    registry=registry
)

active_users_current = Gauge(
    'healthrix_active_users_current',
    'Currently active users',
    registry=registry
)

websocket_connections_active = Gauge(
    'healthrix_websocket_connections_active',
    'Active WebSocket connections',
    registry=registry
)

# ML Model Metrics
ml_predictions_total = Counter(
    'healthrix_ml_predictions_total',
    'Total ML predictions made',
    ['model_type'],
    registry=registry
)

ml_prediction_duration_seconds = Histogram(
    'healthrix_ml_prediction_duration_seconds',
    'ML prediction duration',
    ['model_type'],
    registry=registry
)

anomalies_detected_total = Counter(
    'healthrix_anomalies_detected_total',
    'Total anomalies detected',
    ['severity'],
    registry=registry
)

# Cache Metrics
cache_hits_total = Counter(
    'healthrix_cache_hits_total',
    'Cache hits',
    ['cache_type'],
    registry=registry
)

cache_misses_total = Counter(
    'healthrix_cache_misses_total',
    'Cache misses',
    ['cache_type'],
    registry=registry
)

# Error Metrics
errors_total = Counter(
    'healthrix_errors_total',
    'Total errors',
    ['error_type', 'severity'],
    registry=registry
)


# Decorators for automatic metrics tracking

def track_api_metrics(endpoint: str):
    """
    Decorator to track API endpoint metrics.

    Args:
        endpoint: Endpoint name

    Usage:
        @app.get("/api/v1/activities")
        @track_api_metrics("list_activities")
        async def list_activities():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                raise
            finally:
                duration = time.time() - start_time

                # Get method from request context
                method = "GET"  # Default, would extract from request

                # Record metrics
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()

                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return wrapper
    return decorator


def track_db_query(operation: str, table: str):
    """
    Decorator to track database query metrics.

    Args:
        operation: Database operation (select, insert, update, delete)
        table: Table name

    Usage:
        @track_db_query("select", "activities")
        def get_activities(db: Session):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)

        return wrapper
    return decorator


# Metric recording functions

def record_activity_logged(task_type: str):
    """
    Record an activity being logged.

    Args:
        task_type: Type of task logged
    """
    activities_logged_total.labels(task_type=task_type).inc()


def record_performance_calculation(calc_type: str, duration: float):
    """
    Record a performance calculation.

    Args:
        calc_type: Type of calculation (individual, team, all)
        duration: Calculation duration in seconds
    """
    performance_calculations_total.labels(type=calc_type).inc()
    performance_calculation_duration_seconds.observe(duration)


def record_ml_prediction(model_type: str, duration: float):
    """
    Record an ML prediction.

    Args:
        model_type: Type of ML model used
        duration: Prediction duration in seconds
    """
    ml_predictions_total.labels(model_type=model_type).inc()
    ml_prediction_duration_seconds.labels(model_type=model_type).observe(duration)


def record_anomaly_detected(severity: str):
    """
    Record an anomaly detection.

    Args:
        severity: Anomaly severity (low, medium, high)
    """
    anomalies_detected_total.labels(severity=severity).inc()


def record_cache_access(cache_type: str, hit: bool):
    """
    Record cache access.

    Args:
        cache_type: Type of cache (redis, memory, etc.)
        hit: Whether it was a cache hit
    """
    if hit:
        cache_hits_total.labels(cache_type=cache_type).inc()
    else:
        cache_misses_total.labels(cache_type=cache_type).inc()


def record_error(error_type: str, severity: str = "error"):
    """
    Record an error.

    Args:
        error_type: Type of error
        severity: Error severity (warning, error, critical)
    """
    errors_total.labels(error_type=error_type, severity=severity).inc()


def update_active_users(count: int):
    """
    Update active user count.

    Args:
        count: Current number of active users
    """
    active_users_current.set(count)


def update_websocket_connections(count: int):
    """
    Update WebSocket connection count.

    Args:
        count: Current number of WebSocket connections
    """
    websocket_connections_active.set(count)


def update_db_connections(count: int):
    """
    Update database connection count.

    Args:
        count: Current number of database connections
    """
    db_connections_active.set(count)


# FastAPI endpoint

router = APIRouter()


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus format.
    """
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )


# Example usage
"""
# In your main FastAPI app:

from phase3_enterprise.monitoring.prometheus_exporter import router as metrics_router
from phase3_enterprise.monitoring.prometheus_exporter import (
    record_activity_logged,
    record_performance_calculation,
    track_api_metrics
)

# Include metrics endpoint
app.include_router(metrics_router)

# Use in endpoints:

@app.post("/api/v1/activities")
@track_api_metrics("create_activity")
async def create_activity(activity: ActivityCreate):
    # ... create activity ...

    # Record metric
    record_activity_logged(activity.task_name)

    return activity


@app.post("/api/v1/performance/calculate")
async def calculate_performance(date: str):
    start_time = time.time()

    # ... calculate performance ...

    duration = time.time() - start_time
    record_performance_calculation("team", duration)

    return scores
"""
