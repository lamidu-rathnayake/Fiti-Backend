from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import security
from app.core.security import get_current_user, init_firebase_admin, require_verified_tailor
from app.domain.repositories.profile_repository import AbstractTailorRepository


def test_init_firebase_admin_accepts_json_credentials():
    firebase_app = object()
    secret = SimpleNamespace(
        get_secret_value=lambda: '{"type": "service_account", "project_id": "fiti"}'
    )

    with (
        patch.object(security.settings, "FIREBASE_CREDENTIALS_JSON", secret),
        patch.object(security.firebase_admin, "get_app", side_effect=ValueError),
        patch.object(security.credentials, "Certificate") as certificate,
        patch.object(
            security.firebase_admin, "initialize_app", return_value=firebase_app
        ) as initialize_app,
    ):
        result = init_firebase_admin()

    certificate.assert_called_once_with(
        {"type": "service_account", "project_id": "fiti"}
    )
    initialize_app.assert_called_once_with(certificate.return_value)
    assert result is firebase_app


@pytest.mark.asyncio
async def test_get_current_user_uses_initialized_app():
    firebase_app = object()
    authorization = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid-token"
    )

    with (
        patch.object(security, "init_firebase_admin", return_value=firebase_app),
        patch.object(
            security.auth,
            "verify_id_token",
            return_value={"uid": "user-1", "email": "user@example.com"},
        ) as verify_id_token,
    ):
        user = await get_current_user(authorization)

    verify_id_token.assert_called_once_with("valid-token", app=firebase_app)
    assert user["uid"] == "user-1"


@pytest.mark.asyncio
async def test_get_current_user_redacts_firebase_initialization_failure():
    authorization = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid-token"
    )
    leaked_secret = "private-key-material"

    with patch.object(
        security,
        "init_firebase_admin",
        side_effect=FileNotFoundError(leaked_secret),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(authorization)

    assert exc_info.value.status_code == 503
    assert leaked_secret not in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_verified_tailor_allows_verified_profile():
    repository = AsyncMock(spec=AbstractTailorRepository)
    repository.get_by_id.return_value = SimpleNamespace(is_verified=True)

    uid = await require_verified_tailor("tailor-1", repository)

    assert uid == "tailor-1"


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", [None, SimpleNamespace(is_verified=False)])
async def test_require_verified_tailor_rejects_unverified_or_missing_profile(profile):
    repository = AsyncMock(spec=AbstractTailorRepository)
    repository.get_by_id.return_value = profile

    with pytest.raises(HTTPException) as exc_info:
        await require_verified_tailor("tailor-1", repository)

    assert exc_info.value.status_code == 403
    assert "support@fiti.lk" in exc_info.value.detail