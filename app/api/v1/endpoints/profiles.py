from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_manage_profile_use_case
from app.core.security import get_current_user_uid, require_role
from app.api.schemas.user_schema import (
    ClientRegisterRequest,
    ClientResponse,
    MeasurementProfileRequest,
    MeasurementProfileResponse,
    TailorRegisterRequest,
    TailorResponse,
)
from app.domain.exceptions.user import (
    ClientNotFoundError,
    ProfileAlreadyExistsError,
    TailorNotFoundError,
)
from app.use_cases.dtos.user_dto import (
    ClientRegisterDTO,
    MeasurementProfileDTO,
    TailorRegisterDTO,
)
from app.use_cases.user.manage_profile import ManageProfileUseCase

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# ── Client Registration ─────────────────────────────────────────────────

@router.post("/client", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def register_client(
    request: ClientRegisterRequest,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """
    Register a client profile for an already authenticated Firebase user.
    The Firebase UID is extracted automatically from the verified Bearer Token,
    or read from request.id if explicitly provided.
    """
    profile_id = request.id or authenticated_uid
    try:
        dto = ClientRegisterDTO(id=profile_id)
        result = await use_case.register_client(dto)
        return result
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/client/{client_id}", response_model=ClientResponse)
async def get_client_profile(
    client_id: str,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Get a client's own profile. Requires client role."""
    try:
        return await use_case.get_client_profile(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ── Tailor Registration ─────────────────────────────────────────────────

@router.post("/tailor", response_model=TailorResponse, status_code=status.HTTP_201_CREATED)
async def register_tailor(
    request: TailorRegisterRequest,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """
    Register a tailor profile for an already authenticated Firebase user.
    The Firebase UID is extracted automatically from the verified Bearer Token,
    or read from request.id if explicitly provided.
    NIC images must be uploaded to cloud storage first.
    """
    profile_id = request.id or authenticated_uid
    try:
        dto = TailorRegisterDTO(
            id=profile_id,
            nic_front=request.nic_front,
            nic_rear=request.nic_rear,
        )
        result = await use_case.register_tailor(dto)
        return result
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/tailor/{tailor_id}", response_model=TailorResponse)
async def get_tailor_profile(
    tailor_id: str,
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Get a tailor's public profile. Accessible by any authenticated user (clients browsing tailors)."""
    try:
        return await use_case.get_tailor_profile(tailor_id)
    except TailorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/tailor/{tailor_id}/verification")
async def get_tailor_verification_status(
    tailor_id: str,
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Get a tailor's verification status. Returns is_verified flag."""
    try:
        profile = await use_case.get_tailor_profile(tailor_id)
        return {"tailor_id": tailor_id, "is_verified": profile.is_verified}
    except TailorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ── Measurements ────────────────────────────────────────────────────────

@router.put("/client/{client_id}/measurements", response_model=MeasurementProfileResponse)
async def upsert_measurements(
    client_id: str,
    request: MeasurementProfileRequest,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Save or update standard body measurements for a client profile. Requires client role."""
    dto = MeasurementProfileDTO(
        client_id=client_id,
        chest=request.chest,
        waist=request.waist,
        shoulder=request.shoulder,
        sleeve=request.sleeve,
        neck=request.neck,
        hip=request.hip,
        inseam=request.inseam,
        length=request.length,
        notes=request.notes,
    )
    result = await use_case.upsert_measurement_profile(dto)
    return result


@router.get("/client/{client_id}/measurements", response_model=Optional[MeasurementProfileResponse])
async def get_measurements(
    client_id: str,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Fetch the saved body measurement profile for a client. Requires client role."""
    result = await use_case.get_measurement_profile(client_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No measurement profile found for client '{client_id}'.",
        )
    return result
