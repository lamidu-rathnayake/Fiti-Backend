import json
import logging
import os

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

# Hardcoded Firebase Admin credentials for fiti-b0cb2
DEFAULT_FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "fiti-b0cb2",
    "private_key_id": "0182bfc13393840b3bc90e5089093c3e02938302",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC4IcE9IvyEBiup\nSZghZ+MEY95QyeAAWqfu7OTKBM+AuJfCizFqK9knjufCASGXi7yseKdvz9tk/WY+\nam8nSSBbaekO07he/ECjBaHI3aY2goS4zBTmHB7/cHq9nk1JOsrzj1xi99aR+m5P\nRoVHZqzp5maTCWIEdZe8OJB3Au/YKxQpq8xPSS9bCkJIpSBLdn4qFAEMfOXnbykp\nHCVDRVbEGZCvi1KYQknRCefFOetqqHueVLHtI/78CqHr7jkrd22F4ZL/Lc9iZi+j\nRPKpwcCtrKVREip4j0E7hT/LVogC+x87zwnRhEWNcFPJND5oB04XsbAvBGXQHDIf\nThNZ6bSFAgMBAAECggEABHp9srj5H1TvFuz9UEKwmNi8/YYLdra9wufsIKXBTkYv\nGsI773Mlkvq81FEmugLiEefVWrjZgzlOlVINZg03RkHrMzsfDuBfyhdG+hW6BzVh\neQUttPMWJexcb+Q7yP4vFYF1I8sXYvGOYUs7zqLGreG2uPjPc4BQsnlFuj9OChnn\nkJhOkBKtUJz4sbIg8+GmnpuKCMtvjfq2NzqNUc4x+QnZnRrfHDGlk2ZK6Alpv9aF\nimnprHtM1VicXTUhwfEpAkIJ06p9lYR7oWhte2CqMuREBPTKZ9+EPuX6uU6i8/k9\nTnlMSS2NgB6M2Xtj1PwVllMwJzzTqY9DGaBVU6sZAQKBgQDf/+iSNo9Xj2yeCEc6\n9dsFG5g7HblI+Y/sKM0OcZyzeAFBXM6SpBWCvVxQ1WOTuD4EjcSxD7SQAGJsvmpB\n3C1gqqI8px8xLDWw8iAJfh4gMCib4B3FoCzf3U8eutbhXLp55fNF+QCIkPN1eOCA\nM/bY8q7N/v5mn/DvAVYZ0qvOoQKBgQDSb85IfWKS2bPqfPE5fQS/W95HpUsa729t\ngzyxQsz4N+M01L9I7+CwbKxBcY12pyFUi6vvIqi3yuxZgMnVaSjQPgKdsugxpKxL\no1KzPUgm0zPpH+GLmrm6mKJvjYzHUHXCnG0mDtL3f4f0eMKrMS/YAoSSyB3xUHZR\nbbfm5e3PZQKBgAL/XLBgNIjabXyr5bAfTCAEX4QjALC+TjO91Aimco9gQrwKLuV9\ndqA6Qnr+cAexBntvHju0Vxk6OBb2cVuSQ7Uwc11Way9wRQOqKc2Wt3Z8zn5PgHZ9\njzwrrPxfSbLYV9J7xkagb2Zkci2XQYHVsC71CGvPRr4+062PGgTccdohAoGAEBIj\n0dtphMeFevnxvi8zBp4weo5ADx2MB/QG1Y7Bco9qFaXNufc/1JloClNut0oKPJey\nGMAv3GFt7WPthhPS3xxtPLfmDayCz//4F+ItOXHVvA8IPY4icwKnHRfVUX9ujt89\nYrOtHuOpcV0rmMFX4wpGL6OCzeQUNSHI8qRKphUCgYEAssL5ZqaQ94mjJwWfYMmb\n4SLOO1oQScxToOvFNbuIvcSowMoBOm938cUkz1SN1gTaVGcq37WFh97G/180jOOg\nHKCYLLuH/qrmLZbNiOJElsyTrhK5lTKZZB6ElvIpRLNoL+FkSt/baic9nYbMiFot\nVhzK5r+q/8VIkDn8+8jShKg=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@fiti-b0cb2.iam.gserviceaccount.com",
    "client_id": "108670371509497618879",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40fiti-b0cb2.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}


def init_firebase_admin():
    """Returns the default Firebase Admin app, initializing it when needed."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        raw_cred = (
            settings.FIREBASE_CREDENTIALS_JSON.get_secret_value().strip()
            if settings.FIREBASE_CREDENTIALS_JSON
            else None
        )

        # Strip surrounding quotes if present (e.g. from bash/env exports)
        if raw_cred and (
            (raw_cred.startswith("'") and raw_cred.endswith("'"))
            or (raw_cred.startswith('"') and raw_cred.endswith('"'))
        ):
            raw_cred = raw_cred[1:-1].strip()

        if not raw_cred:
            cred = credentials.Certificate(DEFAULT_FIREBASE_CREDENTIALS)
            app = firebase_admin.initialize_app(cred)
        elif os.path.isfile(raw_cred):
            cred = credentials.Certificate(raw_cred)
            app = firebase_admin.initialize_app(cred)
        else:
            try:
                cred_dict = json.loads(raw_cred)
                cred = credentials.Certificate(cred_dict)
                app = firebase_admin.initialize_app(cred)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "FIREBASE_CREDENTIALS_JSON was invalid (%s). Falling back to default credentials.",
                    type(exc).__name__,
                )
                cred = credentials.Certificate(DEFAULT_FIREBASE_CREDENTIALS)
                app = firebase_admin.initialize_app(cred)

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
