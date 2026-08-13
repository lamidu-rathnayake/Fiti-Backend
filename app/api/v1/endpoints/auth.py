from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import get_current_user_uid
from app.api.dependencies import get_manage_rbac_use_case
from app.use_cases.rbac.manage_rbac import ManageRBACUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RoleCheckResponse(BaseModel):
    uid: str
    roles: list[str]
    redirect_to: str

@router.get("/me/role", response_model=RoleCheckResponse)
async def get_user_role(
    authenticated_uid: str = Depends(get_current_user_uid),
    rbac_use_case: ManageRBACUseCase = Depends(get_manage_rbac_use_case),
):
    """
    Gateway endpoint for post-login redirection.
    Returns the user's role and the appropriate redirect URL.
    """
    overview = await rbac_use_case.get_user_access_overview(authenticated_uid)
    roles = overview.roles
    
    if "admin" in roles:
        # Redirect to the separate Admin Backend
        redirect_to = f"{settings.ADMIN_BACKEND_URL}/dashboard" if settings.ADMIN_BACKEND_URL else "/admin/dashboard"
    elif "tailor" in roles or "seller" in roles:
        # Both tags supported for backward compatibility during transition
        redirect_to = "/seller/dashboard"
    elif "client" in roles:
        redirect_to = "/client/dashboard"
    else:
        # New users without a role yet go to onboarding
        redirect_to = "/onboarding"
        
    return RoleCheckResponse(
        uid=authenticated_uid,
        roles=roles,
        redirect_to=redirect_to
    )
