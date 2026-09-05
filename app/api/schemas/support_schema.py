from datetime import datetime

from pydantic import BaseModel, Field


class NotificationCreateRequest(BaseModel):
    user_id: str = Field(..., description="Firebase Auth UID of the recipient")
    title: str = Field(..., min_length=1, max_length=150)
    message: str | None = Field(None, max_length=2000)


class NotificationResponse(BaseModel):
    notification_id: int
    user_id: str
    title: str
    message: str | None = None
    is_read: bool = False
    created_at: datetime | None = None


class FavoriteShopRequest(BaseModel):
    client_id: str = Field(..., description="Firebase Auth UID of the client")
    shop_id: int


class FavoriteShopResponse(BaseModel):
    favorite_id: int
    client_id: str
    shop_id: int
    created_at: datetime | None = None
