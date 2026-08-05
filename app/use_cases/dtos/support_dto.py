from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotificationCreateDTO:
    user_id: str
    title: str
    message: str | None = None


@dataclass
class NotificationOutputDTO:
    notification_id: int
    user_id: str
    title: str
    message: str | None = None
    is_read: bool = False
    created_at: datetime | None = None


@dataclass
class FavoriteShopCreateDTO:
    client_id: str
    shop_id: int


@dataclass
class FavoriteShopOutputDTO:
    favorite_id: int
    client_id: str
    shop_id: int
    created_at: datetime | None = None
