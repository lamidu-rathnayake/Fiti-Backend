from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_rbac_repository
from app.core.security import get_current_user
from app.domain.repositories.rbac_repository import AbstractRBACRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RoleCheckResponse(BaseModel):
    uid: str
    email: str | None
    role: str


@router.get("/me/role", response_model=RoleCheckResponse)
async def get_user_role(
    user_info: dict = Depends(get_current_user),
    rbac_repo: AbstractRBACRepository = Depends(get_rbac_repository),
):
    """
    Gateway endpoint for role verification.
    Returns the user's UID, email, and role from PostgreSQL.
    Raises HTTP 404 if user has no role registered yet.
    """
    uid = user_info["uid"]
    email = user_info.get("email")
    role = user_info.get("role")

    if not role:
        # Fallback to querying PostgreSQL 'user_roles' table via RBAC repository
        try:
            roles = await rbac_repo.get_user_roles(uid)
            if roles:
                # Assuming one main role per user for the gateway check
                role = roles[0].name
        except Exception:
            pass

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found for user.",
        )

    return RoleCheckResponse(uid=uid, email=email, role=role)
