import time
from typing import Optional, Tuple, Type

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.manager import BaseUserManager
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2

from cnm_bookhub_be.db.models.users import get_user_manager
from cnm_bookhub_be.settings import settings

def get_custom_oauth_router(
    oauth_client: BaseOAuth2,
    backend: AuthenticationBackend,
    state_secret: str,
    associate_by_email: bool = False,
    is_verified_by_default: bool = False,
) -> APIRouter:
    """
    Produce an OAuth router with a custom callback that redirects to Frontend.
    """
    router = APIRouter()
    
    # 1. Authorize logic (Standard)
    @router.get("/authorize", name=f"oauth:{oauth_client.name}.authorize")
    async def authorize(
        request: Request,
        scopes: list[str] = Query(None),
    ) -> dict:
        if scopes:
            authorization_url = await oauth_client.get_authorization_url(
                redirect_uri=str(request.url_for(f"oauth:{oauth_client.name}.callback")),
                state=state_secret,
                scope=scopes,
            )
        else:
            authorization_url = await oauth_client.get_authorization_url(
                redirect_uri=str(request.url_for(f"oauth:{oauth_client.name}.callback")),
                state=state_secret,
            )
            
        return {"authorization_url": authorization_url}

    # 2. Callback logic (Custom Redirect)
    oauth2_authorize_callback = OAuth2AuthorizeCallback(
        oauth_client,
        route_name=f"oauth:{oauth_client.name}.callback",
    )

    @router.get("/callback", name=f"oauth:{oauth_client.name}.callback")
    async def callback(
        request: Request,
        access_token_state: Tuple[dict, str] = Depends(oauth2_authorize_callback),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        try:
            token, state = access_token_state
            account_id = token.get("id_token_claims", {}).get("sub") or token.get("id")
            email = token.get("id_token_claims", {}).get("email") or token.get("email")
            
            if not email:
                 try:
                    account_id, email = await oauth_client.get_id_email(
                        token["access_token"]
                    )
                 except Exception:
                     pass

            if not email:
                 return RedirectResponse(
                     url="http://localhost:8080/Auth/index.html?error=no_email", 
                     status_code=status.HTTP_302_FOUND
                 )

            # --- CALCULATE EXPIRES_AT ---
            expires_at = token.get("expires_at")
            if expires_at is None and "expires_in" in token:
                expires_at = int(time.time()) + int(token["expires_in"])

            # --- CALL OAUTH_CALLBACK WITH KEYWORD ARGS ---
            user = await user_manager.oauth_callback(
                oauth_name=oauth_client.name,
                access_token=token["access_token"],
                account_id=str(account_id),
                account_email=email,
                expires_at=expires_at,
                refresh_token=token.get("refresh_token"),
                request=request,
                associate_by_email=associate_by_email,
                is_verified_by_default=is_verified_by_default
            )
            
            # Create Auth Token
            token_str = await strategy.write_token(user)
            
            # REDIRECT TO FRONTEND
            redirect_url = f"{settings.frontend_url}/Auth/index.html?token={token_str}"
            
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Still returning JSON for now to see the error details if it persists
            return {"error": str(e), "traceback": traceback.format_exc()}

    return router
