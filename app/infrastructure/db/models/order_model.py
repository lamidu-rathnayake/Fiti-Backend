from datetime import UTC, date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.order import (
    Bid,
    ClothingRequest,
    ClothingRequestImage,
    ClothingRequestStatusEnum,
    ClothingRequestTypeEnum,
    FabricStatusEnum,
    Measurement,
    Order,
    OrderStatusEnum,
    Payment,
    PaymentMethodEnum,
    PaymentStatusEnum,
    Rating,
    ServiceTypeEnum,
    ShopRequest,
    ShopRequestStatusEnum,
)
from app.domain.entities.order import Measurement as DomainMeasurement
from app.domain.entities.user import GenderEnum
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user_model import MeasurementProfileModel


class ClothingRequestModel(Base):
    __tablename__ = "clothing_requests"

    request_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    client_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    clothing_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(
        Enum(
            GenderEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        nullable=True,
    )
    fabric_status: Mapped[FabricStatusEnum | None] = mapped_column(
        Enum(
            FabricStatusEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # NEW: URL to audio file stored in Firebase Storage / Azure Blob
    voice_note_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    # NEW: Online vs. physical-visit workflow toggle
    service_type: Mapped[ServiceTypeEnum] = mapped_column(
        Enum(
            ServiceTypeEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        default=ServiceTypeEnum.ONLINE,
        nullable=False,
    )
    # NEW: Direct vs Bidding distinction
    request_type: Mapped[ClothingRequestTypeEnum] = mapped_column(
        Enum(
            ClothingRequestTypeEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        default=ClothingRequestTypeEnum.DIRECT,
        nullable=False,
    )
    request_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ClothingRequestStatusEnum] = mapped_column(
        Enum(
            ClothingRequestStatusEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        default=ClothingRequestStatusEnum.OPEN,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    measurement: Mapped[Optional["MeasurementModel"]] = relationship(
        "MeasurementModel",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan",
    )
    # Optional reference to the client's saved MeasurementProfile (reusable)
    measurement_profile_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("measurement_profile.measurement_id", ondelete="SET NULL"),
        nullable=True,
    )
    measurement_profile: Mapped[Optional["MeasurementProfileModel"]] = relationship(
        "MeasurementProfileModel",
        primaryjoin="MeasurementProfileModel.measurement_id==ClothingRequestModel.measurement_profile_id",
        viewonly=True,
        uselist=False,
    )
    # NEW: Zero-to-many design inspiration images
    design_images: Mapped[list["ClothingRequestImageModel"]] = relationship(
        "ClothingRequestImageModel",
        back_populates="request",
        cascade="all, delete-orphan",
    )
    shop_requests: Mapped[list["ShopRequestModel"]] = relationship(
        "ShopRequestModel",
        back_populates="clothing_request",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> ClothingRequest:
        return ClothingRequest(
            request_id=self.request_id,
            client_id=self.client_id,
            target_date=self.target_date,
            target_budget=self.target_budget,
            clothing_category=self.clothing_category,
            gender=self.gender,
            fabric_status=self.fabric_status,
            description=self.description,
            voice_note_url=self.voice_note_url,
            service_type=self.service_type,
            request_type=self.request_type,
            request_location=self.request_location,
            status=self.status,
            measurement=(
                self.measurement.to_domain()
                if self.measurement
                else (
                    DomainMeasurement(
                        measurement_id=self.measurement_profile.measurement_id,
                        request_id=None,
                        chest=self.measurement_profile.chest,
                        waist=self.measurement_profile.waist,
                        shoulder=self.measurement_profile.shoulder,
                        sleeve=self.measurement_profile.sleeve,
                        neck=self.measurement_profile.neck,
                        hip=self.measurement_profile.hip,
                        inseam=self.measurement_profile.inseam,
                        length=self.measurement_profile.length,
                        notes=self.measurement_profile.notes,
                        created_at=self.measurement_profile.created_at,
                        updated_at=self.measurement_profile.updated_at,
                    )
                    if self.measurement_profile
                    else None
                )
            ),
            design_images=[img.to_domain() for img in self.design_images]
            if self.design_images
            else [],
            shop_requests=[sr.to_domain() for sr in self.shop_requests]
            if self.shop_requests
            else [],
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ClothingRequestImageModel(Base):
    """Stores design inspiration image URLs — files live in cloud storage."""

    __tablename__ = "clothing_request_images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clothing_requests.request_id", ondelete="CASCADE"),
        nullable=False,
    )
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    request: Mapped["ClothingRequestModel"] = relationship(
        "ClothingRequestModel", back_populates="design_images"
    )

    def to_domain(self) -> ClothingRequestImage:
        return ClothingRequestImage(
            image_id=self.image_id,
            request_id=self.request_id,
            image_url=self.image_url,
            created_at=self.created_at,
        )


class MeasurementModel(Base):
    __tablename__ = "measurements"

    measurement_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clothing_requests.request_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    chest: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist: Mapped[float | None] = mapped_column(Float, nullable=True)
    shoulder: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleeve: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip: Mapped[float | None] = mapped_column(Float, nullable=True)
    inseam: Mapped[float | None] = mapped_column(Float, nullable=True)
    length: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    request: Mapped["ClothingRequestModel"] = relationship(
        "ClothingRequestModel", back_populates="measurement"
    )

    def to_domain(self) -> Measurement:
        return Measurement(
            measurement_id=self.measurement_id,
            request_id=self.request_id,
            chest=self.chest,
            waist=self.waist,
            shoulder=self.shoulder,
            sleeve=self.sleeve,
            neck=self.neck,
            hip=self.hip,
            inseam=self.inseam,
            length=self.length,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ShopRequestModel(Base):
    __tablename__ = "shop_requests"
    __table_args__ = (
        UniqueConstraint("request_id", "shop_id", name="uq_request_shop"),
    )

    shop_request_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clothing_requests.request_id", ondelete="CASCADE"),
        nullable=False,
    )
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False
    )
    offered_price: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # latest bid amount
    status: Mapped[ShopRequestStatusEnum] = mapped_column(
        Enum(
            ShopRequestStatusEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        default=ShopRequestStatusEnum.PENDING,
        nullable=False,
    )
    response_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    clothing_request: Mapped["ClothingRequestModel"] = relationship(
        "ClothingRequestModel", back_populates="shop_requests"
    )
    bids: Mapped[list["BidModel"]] = relationship(
        "BidModel", back_populates="shop_request", cascade="all, delete-orphan"
    )

    def to_domain(self) -> ShopRequest:
        return ShopRequest(
            shop_request_id=self.shop_request_id,
            request_id=self.request_id,
            shop_id=self.shop_id,
            offered_price=self.offered_price,
            status=self.status,
            response_date=self.response_date,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class BidModel(Base):
    __tablename__ = "bids"

    bid_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shop_requests.shop_request_id", ondelete="CASCADE"),
        nullable=False,
    )
    bid_amount: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    shop_request: Mapped["ShopRequestModel"] = relationship(
        "ShopRequestModel", back_populates="bids"
    )

    def to_domain(self) -> Bid:
        return Bid(
            bid_id=self.bid_id,
            shop_request_id=self.shop_request_id,
            bid_amount=self.bid_amount,
            message=self.message,
            created_at=self.created_at,
        )


class OrderModel(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shop_requests.shop_request_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    order_status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(
            OrderStatusEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        default=OrderStatusEnum.IN_PROGRESS,
        nullable=False,
    )
    accepted_price: Mapped[float] = mapped_column(Float, nullable=False)
    started_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_domain(self) -> Order:
        return Order(
            order_id=self.order_id,
            shop_request_id=self.shop_request_id,
            order_status=self.order_status,
            accepted_price=self.accepted_price,
            started_date=self.started_date,
            completed_date=self.completed_date,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class PaymentModel(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[PaymentMethodEnum | None] = mapped_column(
        Enum(
            PaymentMethodEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        nullable=True,
    )
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        Enum(
            PaymentStatusEnum,
            values_callable=lambda enum_class: [item.value for item in enum_class],
            native_enum=False,
        ),
        default=PaymentStatusEnum.PENDING,
        nullable=False,
    )
    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    def to_domain(self) -> Payment:
        return Payment(
            payment_id=self.payment_id,
            order_id=self.order_id,
            amount=self.amount,
            payment_method=self.payment_method,
            payment_status=self.payment_status,
            payment_date=self.payment_date,
            created_at=self.created_at,
        )


class RatingModel(Base):
    __tablename__ = "ratings"

    rating_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    client_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    def to_domain(self) -> Rating:
        return Rating(
            rating_id=self.rating_id,
            order_id=self.order_id,
            client_id=self.client_id,
            shop_id=self.shop_id,
            rating=self.rating,
            review=self.review,
            created_at=self.created_at,
        )
