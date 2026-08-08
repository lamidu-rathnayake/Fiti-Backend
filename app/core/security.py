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
            logger.warning(f"Could not initialize Firebase Admin SDK automatically: {exc}")


async def get_current_user_uid(
    auth_header: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """
    Statelessly verifies the Firebase ID Token from the 'Authorization: Bearer <token>' header.

    Option 2 Architecture Flow:
    1. Client signs in directly with Firebase Auth on the web browser.
    2. Client receives a Firebase ID Token.
    3. Client sends request to FastAPI with header: Authorization: Bearer <token>.
    4. Backend cryptographically verifies the token signature using Firebase Admin SDK.
    5. Returns the verified Firebase UID.
    """
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
        try:
            init_firebase_admin()
            decoded_token = auth.verify_id_token(token)
            return decoded_token["uid"]
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired Firebase authentication token: {exc!s}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Fallback mode for testing/local dev when no token is passed in header
    if settings.MOCK_FIREBASE_AUTH or settings.ENVIRONMENT in ("development", "testing"):
        return "mock_firebase_uid"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication token required in Authorization header (Bearer <token>).",
        headers={"WWW-Authenticate": "Bearer"},
    )
