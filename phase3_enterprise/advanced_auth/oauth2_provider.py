"""
OAuth2 / OpenID Connect Authentication
=======================================

Enterprise SSO support for OAuth2 and OIDC providers.

Supported providers:
- Google Workspace
- Microsoft Azure AD
- Okta
- Auth0
- Custom OIDC providers
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
import httpx

router = APIRouter()


class OAuthConfig(BaseModel):
    """OAuth2 provider configuration."""
    provider_name: str
    client_id: str
    client_secret: str
    server_metadata_url: Optional[str] = None
    authorize_url: Optional[str] = None
    access_token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    scopes: list[str] = ["openid", "profile", "email"]


class OAuthProvider:
    """
    OAuth2/OIDC provider manager.

    Handles authentication flows for multiple providers.
    """

    def __init__(self):
        """Initialize OAuth provider."""
        self.oauth = OAuth()
        self.providers: Dict[str, Any] = {}

    def register_provider(self, config: OAuthConfig):
        """
        Register an OAuth2/OIDC provider.

        Args:
            config: Provider configuration
        """
        if config.server_metadata_url:
            # Auto-discover from OIDC metadata
            self.oauth.register(
                name=config.provider_name,
                client_id=config.client_id,
                client_secret=config.client_secret,
                server_metadata_url=config.server_metadata_url,
                client_kwargs={'scope': ' '.join(config.scopes)},
            )
        else:
            # Manual configuration
            self.oauth.register(
                name=config.provider_name,
                client_id=config.client_id,
                client_secret=config.client_secret,
                authorize_url=config.authorize_url,
                access_token_url=config.access_token_url,
                userinfo_url=config.userinfo_url,
                client_kwargs={'scope': ' '.join(config.scopes)},
            )

        self.providers[config.provider_name] = config

    def get_provider(self, provider_name: str):
        """Get registered OAuth provider."""
        return self.oauth.create_client(provider_name)

    async def get_user_info(self, provider_name: str, token: dict) -> dict:
        """
        Get user information from OAuth provider.

        Args:
            provider_name: Provider name
            token: OAuth token

        Returns:
            User information dictionary
        """
        provider = self.get_provider(provider_name)

        if hasattr(provider, 'userinfo'):
            # OIDC provider with userinfo endpoint
            user_info = await provider.userinfo(token=token)
        else:
            # Fetch user info from custom endpoint
            config = self.providers[provider_name]
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config.userinfo_url,
                    headers={'Authorization': f"Bearer {token['access_token']}"}
                )
                user_info = response.json()

        return user_info


# Global OAuth provider instance
oauth_provider = OAuthProvider()


# Pre-configured providers
def setup_google_oauth(client_id: str, client_secret: str):
    """Configure Google OAuth2."""
    config = OAuthConfig(
        provider_name="google",
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        scopes=["openid", "email", "profile"]
    )
    oauth_provider.register_provider(config)


def setup_microsoft_oauth(client_id: str, client_secret: str, tenant_id: str = "common"):
    """Configure Microsoft Azure AD OAuth2."""
    config = OAuthConfig(
        provider_name="microsoft",
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url=f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration",
        scopes=["openid", "email", "profile"]
    )
    oauth_provider.register_provider(config)


def setup_okta_oauth(client_id: str, client_secret: str, domain: str):
    """Configure Okta OAuth2."""
    config = OAuthConfig(
        provider_name="okta",
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url=f"https://{domain}/.well-known/openid-configuration",
        scopes=["openid", "email", "profile"]
    )
    oauth_provider.register_provider(config)


# API Endpoints

@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Initiate OAuth2 login flow.

    Args:
        provider: OAuth provider name (google, microsoft, okta, etc.)
        request: FastAPI request

    Returns:
        Redirect to OAuth provider authorization page
    """
    try:
        client = oauth_provider.get_provider(provider)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    # Generate redirect URI
    redirect_uri = request.url_for('oauth_callback', provider=provider)

    # Redirect to provider's authorization page
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}")
async def oauth_callback(provider: str, request: Request):
    """
    OAuth2 callback endpoint.

    Handles the callback from OAuth provider and completes authentication.

    Args:
        provider: OAuth provider name
        request: FastAPI request with authorization code

    Returns:
        User information and access token
    """
    try:
        client = oauth_provider.get_provider(provider)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    # Exchange authorization code for access token
    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")

    # Get user information
    user_info = await oauth_provider.get_user_info(provider, token)

    # TODO: Create or update user in database
    # TODO: Generate JWT token for the application
    # TODO: Redirect to frontend with token

    return {
        "provider": provider,
        "user_info": user_info,
        "access_token": token.get("access_token"),
        "id_token": token.get("id_token"),
    }


@router.post("/link-account")
async def link_oauth_account(
    provider: str,
    oauth_token: str,
    current_user_id: str  # From JWT token
):
    """
    Link an OAuth account to existing user.

    Args:
        provider: OAuth provider name
        oauth_token: OAuth access token
        current_user_id: Current authenticated user ID

    Returns:
        Success message
    """
    # Get user info from OAuth provider
    user_info = await oauth_provider.get_user_info(provider, {"access_token": oauth_token})

    # TODO: Store OAuth provider ID in user record
    # TODO: Handle account linking logic

    return {
        "message": f"Successfully linked {provider} account",
        "provider": provider,
        "provider_user_id": user_info.get("sub") or user_info.get("id")
    }


# Example usage configuration
"""
# In your main FastAPI app:

from phase3_enterprise.advanced_auth.oauth2_provider import (
    router as oauth_router,
    setup_google_oauth,
    setup_microsoft_oauth,
)

# Configure providers
setup_google_oauth(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
)

setup_microsoft_oauth(
    client_id=os.getenv("MICROSOFT_CLIENT_ID"),
    client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
    tenant_id=os.getenv("MICROSOFT_TENANT_ID", "common")
)

# Include router
app.include_router(oauth_router, prefix="/api/v1/oauth", tags=["OAuth"])
"""
