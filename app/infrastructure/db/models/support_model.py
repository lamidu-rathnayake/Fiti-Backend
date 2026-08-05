from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.support import FavoriteShop, Notification
from app.infrastructure.db.base import Base


class FavoriteShopModel(Base):
    __tablename__ = "favorite_shops"
    __table_args__ = (UniqueConstraint("client_id", "shop_id", name="uq_client_shop_fav"),)

    favorite_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(String(128), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    def to_domain(self) -> FavoriteShop:
        return FavoriteShop(
            favorite_id=self.favorite_id,
            client_id=self.client_id,
            shop_id=self.shop_id,
            created_at=self.created_at,
        )


class NotificationModel(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # firebase_uid holds the Firebase Auth UID — no FK to a users table
    firebase_uid: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    def to_domain(self) -> Notification:
        return Notification(
            notification_id=self.notification_id,
            user_id=self.firebase_uid,
            title=self.title,
            message=self.message,
            is_read=self.is_read,
            created_at=self.created_at,
        )
