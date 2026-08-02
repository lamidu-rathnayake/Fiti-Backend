from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.support import FavoriteShop, Notification


class AbstractNotificationRepository(ABC):
    @abstractmethod
    async def create_notification(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: str) -> List[Notification]:
        pass

    @abstractmethod
    async def mark_read(self, notification_id: int) -> bool:
        pass


class AbstractFavoriteShopRepository(ABC):
    @abstractmethod
    async def add_favorite(self, favorite: FavoriteShop) -> FavoriteShop:
        pass

    @abstractmethod
    async def remove_favorite(self, client_id: str, shop_id: int) -> bool:
        pass

    @abstractmethod
    async def list_favorites_by_client(self, client_id: str) -> List[FavoriteShop]:
        pass
