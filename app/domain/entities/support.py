from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FavoriteShop:
    favorite_id: Optional[int]
    client_id: str
    shop_id: int
    created_at: Optional[datetime] = None


@dataclass
class Notification:
    notification_id: Optional[int]
    user_id: str
    title: str
    message: Optional[str] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
