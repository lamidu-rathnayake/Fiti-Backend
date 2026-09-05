from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.shop import Gig, Shop, ShopWork
from app.infrastructure.db.base import Base


class ShopModel(Base):
    __tablename__ = "shops"

    shop_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tailor_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("tailors.id", ondelete="CASCADE"),
        nullable=False,
    )
    shop_name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str | None] = mapped_column(Text, nullable=True)
    shop_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    shop_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    works: Mapped[list["ShopWorkModel"]] = relationship(
        "ShopWorkModel",
        back_populates="shop",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    gigs: Mapped[list["GigModel"]] = relationship(
        "GigModel", back_populates="shop", cascade="all, delete-orphan", lazy="selectin"
    )

    def to_domain(self) -> Shop:
        return Shop(
            shop_id=self.shop_id,
            tailor_id=self.tailor_id,
            shop_name=self.shop_name,
            specialty=self.specialty,
            shop_bio=self.shop_bio,
            shop_address=self.shop_address,
            city=self.city,
            contact_number=self.contact_number,
            registration_number=self.registration_number,
            latitude=self.latitude,
            longitude=self.longitude,
            profile_image_url=self.profile_image_url,
            average_rating=self.average_rating,
            works=[work.to_domain() for work in self.works] if self.works else [],
            gigs=[gig.to_domain() for gig in self.gigs] if self.gigs else [],
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ShopWorkModel(Base):
    __tablename__ = "shop_works"

    work_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    shop: Mapped["ShopModel"] = relationship("ShopModel", back_populates="works")

    def to_domain(self) -> ShopWork:
        return ShopWork(
            work_id=self.work_id,
            shop_id=self.shop_id,
            image_url=self.image_url,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class GigModel(Base):
    __tablename__ = "gigs"

    gig_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )

    shop: Mapped["ShopModel"] = relationship("ShopModel", back_populates="gigs")

    def to_domain(self) -> Gig:
        return Gig(
            gig_id=self.gig_id,
            shop_id=self.shop_id,
            title=self.title,
            description=self.description,
            price=self.price,
            delivery_time=self.delivery_time,
            category=self.category,
            image_url=self.image_url,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
