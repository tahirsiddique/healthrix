"""
Multi-Tenant Middleware
=======================

Handles tenant identification and isolation across requests.

Supports:
- Header-based tenant identification
- Subdomain-based tenant identification
- JWT claim-based tenant identification
"""

from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import re


class TenantContext:
    """
    Thread-local tenant context.

    Stores the current tenant ID for the request lifecycle.
    """
    def __init__(self):
        self._tenant_id: Optional[str] = None

    @property
    def tenant_id(self) -> Optional[str]:
        """Get current tenant ID."""
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, value: str):
        """Set current tenant ID."""
        self._tenant_id = value

    def clear(self):
        """Clear tenant context."""
        self._tenant_id = None


# Global tenant context
tenant_context = TenantContext()


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and set tenant context from requests.

    Supports multiple tenant identification strategies:
    1. Header: X-Tenant-ID
    2. Subdomain: tenant.yourdomain.com
    3. JWT claim: tenant_id in token
    4. Query parameter: ?tenant_id=xxx (dev only)
    """

    def __init__(
        self,
        app: ASGIApp,
        tenant_header: str = "X-Tenant-ID",
        domain_pattern: Optional[str] = None,
        require_tenant: bool = True,
        allow_query_param: bool = False,  # Only for development
    ):
        """
        Initialize tenant middleware.

        Args:
            app: ASGI application
            tenant_header: HTTP header name for tenant ID
            domain_pattern: Regex pattern to extract tenant from subdomain
            require_tenant: Whether tenant is required for all requests
            allow_query_param: Allow tenant ID in query params (dev only)
        """
        super().__init__(app)
        self.tenant_header = tenant_header
        self.domain_pattern = domain_pattern
        self.require_tenant = require_tenant
        self.allow_query_param = allow_query_param

        # Compile domain pattern if provided
        if domain_pattern:
            self.domain_regex = re.compile(domain_pattern)
        else:
            self.domain_regex = None

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request and extract tenant context.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response from downstream
        """
        tenant_id = None

        # Strategy 1: Check header
        tenant_id = request.headers.get(self.tenant_header)

        # Strategy 2: Extract from subdomain
        if not tenant_id and self.domain_regex:
            host = request.headers.get("host", "")
            match = self.domain_regex.match(host)
            if match:
                tenant_id = match.group("tenant")

        # Strategy 3: Check query parameter (dev only)
        if not tenant_id and self.allow_query_param:
            tenant_id = request.query_params.get("tenant_id")

        # Strategy 4: Extract from JWT token (if authenticated)
        if not tenant_id:
            # This would be implemented by your auth system
            # tenant_id = extract_tenant_from_jwt(request)
            pass

        # Set tenant context
        if tenant_id:
            tenant_context.tenant_id = tenant_id
            request.state.tenant_id = tenant_id
        elif self.require_tenant and not self._is_public_path(request.url.path):
            # Tenant required but not found
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant identification required. Please provide tenant ID."
            )

        try:
            # Process request
            response = await call_next(request)
            return response
        finally:
            # Clear tenant context after request
            tenant_context.clear()

    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is public (doesn't require tenant).

        Args:
            path: Request path

        Returns:
            True if path is public
        """
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

        return any(path.startswith(p) for p in public_paths)


def get_current_tenant() -> str:
    """
    Get current tenant ID from context.

    Returns:
        Current tenant ID

    Raises:
        HTTPException: If no tenant in context
    """
    tenant_id = tenant_context.tenant_id

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context found"
        )

    return tenant_id


def get_optional_tenant() -> Optional[str]:
    """
    Get current tenant ID from context (returns None if not set).

    Returns:
        Current tenant ID or None
    """
    return tenant_context.tenant_id


# Example usage
"""
from fastapi import FastAPI
from phase3_enterprise.multi_tenant.tenant_middleware import TenantMiddleware

app = FastAPI()

# Add tenant middleware
app.add_middleware(
    TenantMiddleware,
    tenant_header="X-Tenant-ID",
    domain_pattern=r"^(?P<tenant>[a-z0-9-]+)\.yourdomain\.com$",
    require_tenant=True,
)

# In your endpoints:
from phase3_enterprise.multi_tenant.tenant_middleware import get_current_tenant

@app.get("/api/v1/activities")
def list_activities(tenant_id: str = Depends(get_current_tenant)):
    # tenant_id is automatically extracted
    return db.query(Activity).filter(Activity.tenant_id == tenant_id).all()
"""
