from fastapi import APIRouter, Depends
from firebase_admin import firestore
from pydantic import BaseModel

from app.core.security import get_current_user, init_firebase_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RoleCheckResponse(BaseModel):
    uid: str
    email: str | None
    role: str
    redirect_to: str


@router.get("/me/role", response_model=RoleCheckResponse)
async def get_user_role(
    user_info: dict = Depends(get_current_user),
):
    """
    Gateway endpoint for post-login redirection.
    Returns the user's UID, email, role, and the appropriate redirect URL.
    """
    uid = user_info["uid"]
    email = user_info.get("email")
    role = user_info.get("role")

    if not role:
        try:
            init_firebase_admin()
            db = firestore.client()
            user_doc = db.collection("users").document(uid).get()
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                role = user_data.get("role", "client")
        except Exception:
            role = "client"

    if role == "seller" or role == "tailor":
        redirect_to = "/seller/dashboard"
    elif role == "client":
        redirect_to = "/client/home"
    else:
        redirect_to = "/register"

    return RoleCheckResponse(
        uid=uid, email=email, role=role or "client", redirect_to=redirect_to
    )
