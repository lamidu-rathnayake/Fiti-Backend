import logging

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from app.core.config import settings

logger = logging.getLogger(__name__)

# HTTPBearer security scheme for Swagger UI and header parsing
bearer_scheme = HTTPBearer(auto_error=False)

_firebase_app_initialized = False


def init_firebase_admin():
    """Initializes the Firebase Admin SDK if not already initialized."""
    global _firebase_app_initialized
    if not _firebase_app_initialized and not firebase_admin._apps:
        try:
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
            _firebase_app_initialized = True
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as exc:
            logger.warning(
                f"Could not initialize Firebase Admin SDK automatically: {exc}"
            )


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
            init_firebase_admin()
            decoded_token = auth.verify_id_token(token)
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

    # Mock mode — ONLY when explicitly enabled in .env for local development
    if settings.MOCK_FIREBASE_AUTH:
        logger.warning("MOCK_FIREBASE_AUTH is enabled — bypassing token verification.")
        return {
            "uid": "mock_firebase_uid",
            "email": "mock@example.com",
            "role": "client",
            "name": "Mock User",
            "picture": None,
        }

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

        if settings.MOCK_FIREBASE_AUTH:
            return uid

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
