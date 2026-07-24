from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_create_user_use_case,
    get_user_by_id_use_case,
    get_list_users_use_case,
)
from app.api.schemas.user_schema import UserCreateRequest, UserResponse
from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.use_cases.dtos.user_dto import UserCreateInputDTO
from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user import GetUserUseCase
from app.use_cases.user.list_users import ListUsersUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    try:
        dto = UserCreateInputDTO(
            email=request.email,
            username=request.username,
            password=request.password,
        )
        result = await use_case.execute(dto)
        return result
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    use_case: GetUserUseCase = Depends(get_user_by_id_use_case),
):
    try:
        return await use_case.execute(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
):
    return await use_case.execute(skip=skip, limit=limit)
