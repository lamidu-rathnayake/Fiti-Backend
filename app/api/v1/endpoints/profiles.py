from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_manage_profile_use_case
from app.core.security import get_current_user_uid
from app.api.schemas.user_schema import (
    ClientRegisterRequest,
    ClientResponse,
    MeasurementProfileRequest,
    MeasurementProfileResponse,
    SellerRegisterRequest,
    SellerResponse,
)
from app.domain.exceptions.user import ProfileAlreadyExistsError
from app.use_cases.dtos.user_dto import (
    ClientRegisterDTO,
    MeasurementProfileDTO,
    SellerRegisterDTO,
)
from app.use_cases.user.manage_profile import ManageProfileUseCase

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("/client", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def register_client(
    request: ClientRegisterRequest,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """
    Register a client profile for an already authenticated Firebase user.
    Option 2 Flow: The Firebase UID is extracted automatically from the verified Bearer Token,
    or read from request.id.
    """
    profile_id = request.id or authenticated_uid
    try:
        dto = ClientRegisterDTO(id=profile_id)
        result = await use_case.register_client(dto)
        return result
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/seller", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
async def register_seller(
    request: SellerRegisterRequest,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """
    Register a seller/tailor profile for an already authenticated Firebase user.
    Option 2 Flow: The Firebase UID is extracted automatically from the verified Bearer Token,
    or read from request.id. NIC images must be uploaded to cloud storage first.
    """
    profile_id = request.id or authenticated_uid
    try:
        dto = SellerRegisterDTO(
            id=profile_id,
            nic_front=request.nic_front,
            nic_rear=request.nic_rear,
        )
        result = await use_case.register_seller(dto)
        return result
    except ProfileAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.put("/client/{client_id}/measurements", response_model=MeasurementProfileResponse)
async def upsert_measurements(
    client_id: str,
    request: MeasurementProfileRequest,
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Save or update standard body measurements for a client profile."""
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
    use_case: ManageProfileUseCase = Depends(get_manage_profile_use_case),
):
    """Fetch the saved body measurement profile for a client."""
    result = await use_case.get_measurement_profile(client_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No measurement profile found for client '{client_id}'.",
        )
    return result
