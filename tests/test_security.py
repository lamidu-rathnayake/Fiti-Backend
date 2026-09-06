from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.core.security import require_verified_tailor
from app.domain.repositories.profile_repository import AbstractTailorRepository


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