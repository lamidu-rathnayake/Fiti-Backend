from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.domain.entities.shop import Shop, ShopImage


class ShopModel(Base):
    __tablename__ = "shops"

    shop_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[str] = mapped_column(String(128), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    shop_name: Mapped[str] = mapped_column(String(150), nullable=False)
    shop_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shop_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    images: Mapped[List["ShopImageModel"]] = relationship(
        "ShopImageModel", back_populates="shop", cascade="all, delete-orphan"
    )

    def to_domain(self) -> Shop:
        return Shop(
            shop_id=self.shop_id,
            seller_id=self.seller_id,
            shop_name=self.shop_name,
            shop_bio=self.shop_bio,
            shop_address=self.shop_address,
            city=self.city,
            contact_number=self.contact_number,
            registration_number=self.registration_number,
            latitude=self.latitude,
            longitude=self.longitude,
            average_rating=self.average_rating,
            images=[img.to_domain() for img in self.images] if self.images else [],
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ShopImageModel(Base):
    __tablename__ = "shop_images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    shop: Mapped["ShopModel"] = relationship("ShopModel", back_populates="images")

    def to_domain(self) -> ShopImage:
        return ShopImage(
            image_id=self.image_id,
            shop_id=self.shop_id,
            image_url=self.image_url,
            created_at=self.created_at,
        )
