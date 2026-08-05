from dataclasses import dataclass
from datetime import datetime


@dataclass
class FavoriteShop:
    favorite_id: int | None
    client_id: str
    shop_id: int
    created_at: datetime | None = None


@dataclass
class Notification:
    notification_id: int | None
    user_id: str
    title: str
    message: str = None
    is_read: bool = False
    created_at: datetime = None
