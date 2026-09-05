from app.domain.entities.support import FavoriteShop, Notification
from app.domain.repositories.notification_repository import (
    AbstractFavoriteShopRepository,
    AbstractNotificationRepository,
)
from app.use_cases.dtos.support_dto import (
    FavoriteShopCreateDTO,
    FavoriteShopOutputDTO,
    NotificationCreateDTO,
    NotificationOutputDTO,
)


class ManageSupportUseCase:
    """Handles notifications and favorite-shop operations."""

    def __init__(
        self,
        notification_repository: AbstractNotificationRepository,
        favorite_shop_repository: AbstractFavoriteShopRepository,
    ):
        self.notification_repository = notification_repository
        self.favorite_shop_repository = favorite_shop_repository

    # ── Notifications ──────────────────────────────────────────────────

    async def create_notification(
        self, dto: NotificationCreateDTO
    ) -> NotificationOutputDTO:
        entity = Notification(
            notification_id=None,
            user_id=dto.user_id,
            title=dto.title,
            message=dto.message,
        )
        saved = await self.notification_repository.create_notification(entity)
        return self._to_notification_dto(saved)

    async def list_notifications(self, user_id: str) -> list[NotificationOutputDTO]:
        notifications = await self.notification_repository.list_by_user(user_id)
        return [self._to_notification_dto(n) for n in notifications]

    async def mark_notification_read(self, notification_id: int) -> bool:
        return await self.notification_repository.mark_read(notification_id)

    # ── Favorite Shops ─────────────────────────────────────────────────

    async def add_favorite(self, dto: FavoriteShopCreateDTO) -> FavoriteShopOutputDTO:
        entity = FavoriteShop(
            favorite_id=None,
            client_id=dto.client_id,
            shop_id=dto.shop_id,
        )
        saved = await self.favorite_shop_repository.add_favorite(entity)
        return self._to_favorite_dto(saved)

    async def remove_favorite(self, client_id: str, shop_id: int) -> bool:
        return await self.favorite_shop_repository.remove_favorite(client_id, shop_id)

    async def list_favorites(self, client_id: str) -> list[FavoriteShopOutputDTO]:
        favorites = await self.favorite_shop_repository.list_favorites_by_client(
            client_id
        )
        return [self._to_favorite_dto(f) for f in favorites]

    # ── Private Helpers ────────────────────────────────────────────────

    def _to_notification_dto(self, n: Notification) -> NotificationOutputDTO:
        return NotificationOutputDTO(
            notification_id=n.notification_id,  # type: ignore
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at,
        )

    def _to_favorite_dto(self, f: FavoriteShop) -> FavoriteShopOutputDTO:
        return FavoriteShopOutputDTO(
            favorite_id=f.favorite_id,  # type: ignore
            client_id=f.client_id,
            shop_id=f.shop_id,
            created_at=f.created_at,
        )
