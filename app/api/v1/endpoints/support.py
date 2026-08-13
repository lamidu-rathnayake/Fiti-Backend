from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_manage_support_use_case
from app.api.schemas.support_schema import (
    FavoriteShopRequest,
    FavoriteShopResponse,
    NotificationCreateRequest,
    NotificationResponse,
)
from app.use_cases.dtos.support_dto import (
    FavoriteShopCreateDTO,
    NotificationCreateDTO,
)
from app.use_cases.support.manage_support import ManageSupportUseCase

router = APIRouter(prefix="/support", tags=["Support"])


# ── Notifications ──────────────────────────────────────────────────────


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    request: NotificationCreateRequest,
    use_case: ManageSupportUseCase = Depends(get_manage_support_use_case),
):
    dto = NotificationCreateDTO(
        user_id=request.user_id,
        title=request.title,
        message=request.message,
    )
    return await use_case.create_notification(dto)


@router.get("/notifications/{user_id}", response_model=list[NotificationResponse])
async def list_notifications(
    user_id: str,
    use_case: ManageSupportUseCase = Depends(get_manage_support_use_case),
):
    """List all notifications for a user, newest first."""
    return await use_case.list_notifications(user_id)


@router.patch(
    "/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT
)
async def mark_notification_read(
    notification_id: int,
    use_case: ManageSupportUseCase = Depends(get_manage_support_use_case),
):
    success = await use_case.mark_notification_read(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found.",
        )


# ── Favorite Shops ─────────────────────────────────────────────────────


@router.post(
    "/favorites",
    response_model=FavoriteShopResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite(
    request: FavoriteShopRequest,
    use_case: ManageSupportUseCase = Depends(get_manage_support_use_case),
):
    dto = FavoriteShopCreateDTO(client_id=request.client_id, shop_id=request.shop_id)
    return await use_case.add_favorite(dto)


@router.delete(
    "/favorites/{client_id}/{shop_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_favorite(
    client_id: str,
    shop_id: int,
    use_case: ManageSupportUseCase = Depends(get_manage_support_use_case),
):
    success = await use_case.remove_favorite(client_id, shop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found.",
        )


@router.get("/favorites/{client_id}", response_model=list[FavoriteShopResponse])
async def list_favorites(
    client_id: str,
    use_case: ManageSupportUseCase = Depends(get_manage_support_use_case),
):
    return await use_case.list_favorites(client_id)
