import json
import logging

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from app.api.dependencies import get_tailor_repository
from app.core.config import settings
from app.domain.repositories.profile_repository import AbstractTailorRepository

logger = logging.getLogger(__name__)

# HTTPBearer security scheme for Swagger UI and header parsing
bearer_scheme = HTTPBearer(auto_error=False)

def init_firebase_admin():
    """Returns the default Firebase Admin app, initializing it when needed."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        credentials_json = (
            settings.FIREBASE_CREDENTIALS_JSON.get_secret_value()
            if settings.FIREBASE_CREDENTIALS_JSON
            else None
        )

        if credentials_json:
            cred = credentials.Certificate(json.loads(credentials_json))
            app = firebase_admin.initialize_app(cred)
        else:
            app = firebase_admin.initialize_app()
        logger.info("Firebase Admin SDK initialized successfully.")
        return app


async def get_current_user(
    auth_header: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """
    Statelessly verifies the Firebase ID Token from the 'Authorization: Bearer <token>' header.
    Decodes and returns user info dictionary containing uid, email, and role.
    """
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
        try:
            firebase_app = init_firebase_admin()
        except Exception as exc:
            logger.error(
                "Firebase Admin SDK initialization failed (%s).",
                type(exc).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase authentication service is not configured correctly.",
            ) from exc

        try:
            decoded_token = auth.verify_id_token(token, app=firebase_app)
            return {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "role": decoded_token.get("role"),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
            }
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired Firebase authentication token: {exc!s}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication token required in Authorization header (Bearer <token>).",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_uid(
    user_info: dict = Depends(get_current_user),
) -> str:
    """
    Extracts and returns the verified Firebase UID string from the current user payload.
    """
    return user_info["uid"]


def require_role(role_name: str):
    """
    Dependency factory that verifies a Firebase token AND checks the user holds the required role.
    Role is verified either from JWT token custom claims or from the PostgreSQL 'user_roles' table.
    Firestore DB is no longer used for role checks.
    """
    # Local import to avoid circular dependency
    from app.api.dependencies import get_rbac_repository
    from app.domain.repositories.rbac_repository import AbstractRBACRepository

    async def _check_role(
        user_info: dict = Depends(get_current_user),
        rbac_repo: AbstractRBACRepository = Depends(get_rbac_repository)
    ) -> str:
        uid = user_info["uid"]
        token_role = user_info.get("role")

        # 1. Verify role directly from JWT payload/claims if present
        if token_role:
            if token_role == role_name:
                return uid
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: '{role_name}'. Your role: '{token_role}'.",
                )

        # 2. Fallback: Verify role from PostgreSQL user_roles table
        try:
            roles = await rbac_repo.get_user_roles(uid)
            role_names = [r.name for r in roles]

            if role_name not in role_names:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: '{role_name}'. Your roles: {role_names or 'none'}.",
                )
            return uid
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Error checking PostgreSQL role for UID {uid}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Role verification failed: {exc!s}",
            )

    return _check_role


async def require_verified_tailor(
    authenticated_uid: str = Depends(require_role("tailor")),
    tailor_repo: AbstractTailorRepository = Depends(get_tailor_repository),
) -> str:
    tailor = await tailor_repo.get_by_id(authenticated_uid)
    if not tailor or not tailor.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your account is not verified. Please contact the Fiti team "
                "at support@fiti.lk."
            ),
        )
    return authenticated_uid
