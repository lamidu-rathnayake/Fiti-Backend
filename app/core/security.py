import logging

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials, firestore

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
        return {"uid": "mock_firebase_uid", "email": "mock@example.com", "role": "client"}

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
    Role is verified either from JWT token custom claims or from Firestore DB ('users' collection).
    No PostgreSQL user/role table is used.
    """

    async def _check_role(
        user_info: dict = Depends(get_current_user),
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

        # 2. Fallback: Verify role from Firestore DB users collection
        try:
            init_firebase_admin()
            db = firestore.client()
            user_doc = db.collection("users").document(uid).get()

            if not user_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User profile for UID '{uid}' not found in Firestore DB.",
                )

            user_data = user_doc.to_dict() or {}
            db_role = user_data.get("role")

            if db_role != role_name:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: '{role_name}'. Your role: '{db_role or 'none'}'.",
                )
            return uid
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Error checking Firestore role for UID {uid}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Role verification failed: {exc!s}",
            )

    return _check_role
