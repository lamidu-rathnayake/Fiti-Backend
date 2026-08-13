from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user_uid
from app.api.dependencies import get_manage_rbac_use_case
from app.api.schemas.rbac_schema import (
    RoleAssignRequest,
    UserAccessOverviewResponse,
)
from app.domain.exceptions.rbac import AccessDeniedError, RoleNotFoundError
from app.use_cases.dtos.rbac_dto import RoleAssignDTO
from app.use_cases.rbac.manage_rbac import ManageRBACUseCase

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.post("/assign-role", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role(
    request: RoleAssignRequest,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageRBACUseCase = Depends(get_manage_rbac_use_case),
):
    """Assign a role to a user by Firebase UID."""
    try:
        dto = RoleAssignDTO(user_id=request.user_id, role_name=request.role_name)
        await use_case.assign_role(dto)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/users/{user_id}/access", response_model=UserAccessOverviewResponse)
async def get_user_access(
    user_id: str,
    use_case: ManageRBACUseCase = Depends(get_manage_rbac_use_case),
):
    """Retrieve a user's roles and accessible sections."""
    return await use_case.get_user_access_overview(user_id)


@router.get("/users/{user_id}/check-route")
async def check_route_access(
    user_id: str,
    route_name: str,
    use_case: ManageRBACUseCase = Depends(get_manage_rbac_use_case),
):
    """Verify whether a user has access to a specific route."""
    try:
        await use_case.verify_user_route_access(user_id, route_name)
        return {"has_access": True}
    except AccessDeniedError:
        return {"has_access": False}
