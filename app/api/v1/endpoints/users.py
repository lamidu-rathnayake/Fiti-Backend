from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_create_user_use_case,
    get_user_by_id_use_case,
    get_list_users_use_case,
    get_manage_measurement_use_case,
)
from app.api.schemas.user_schema import (
    UserCreateRequest,
    UserResponse,
    MeasurementProfileRequest,
    MeasurementProfileResponse,
)
from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.use_cases.dtos.user_dto import UserCreateInputDTO, MeasurementProfileDTO
from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user import GetUserUseCase
from app.use_cases.user.list_users import ListUsersUseCase
from app.use_cases.user.manage_measurement import ManageMeasurementProfileUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    try:
        dto = UserCreateInputDTO(
            id=request.id,
            name=request.name,
            email=request.email,
            auth_provider=request.auth_provider,
            whatsapp_number=request.whatsapp_number,
            address=request.address,
            city=request.city,
            postal_code=request.postal_code,
            gender=request.gender,
            age=request.age,
            profile_image=request.profile_image,
            role=request.role,
        )
        return await use_case.execute(dto)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    use_case: GetUserUseCase = Depends(get_user_by_id_use_case),
):
    try:
        return await use_case.execute(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
):
    return await use_case.execute(skip=skip, limit=limit)


@router.put("/{user_id}/measurements", response_model=MeasurementProfileResponse)
async def update_user_measurements(
    user_id: str,
    request: MeasurementProfileRequest,
    use_case: ManageMeasurementProfileUseCase = Depends(get_manage_measurement_use_case),
):
    dto = MeasurementProfileDTO(
        user_id=user_id,
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
    return await use_case.upsert_profile(dto)


@router.get("/{user_id}/measurements", response_model=MeasurementProfileResponse)
async def get_user_measurements(
    user_id: str,
    use_case: ManageMeasurementProfileUseCase = Depends(get_manage_measurement_use_case),
):
    res = await use_case.get_profile(user_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement profile not found")
    return res
