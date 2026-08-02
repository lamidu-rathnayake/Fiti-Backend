from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.domain.entities.user import User, Client, Seller, MeasurementProfile, GenderEnum


class UserModel(Base):
    """SQLAlchemy ORM Model for users table."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(Enum(GenderEnum, native_enum=False), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            name=self.name,
            email=self.email,
            auth_provider=self.auth_provider,
            whatsapp_number=self.whatsapp_number,
            address=self.address,
            city=self.city,
            postal_code=self.postal_code,
            gender=self.gender,
            age=self.age,
            profile_image=self.profile_image,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            auth_provider=user.auth_provider,
            whatsapp_number=user.whatsapp_number,
            address=user.address,
            city=user.city,
            postal_code=user.postal_code,
            gender=user.gender,
            age=user.age,
            profile_image=user.profile_image,
            is_active=user.is_active,
        )


class ClientModel(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(128), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> Client:
        return Client(id=self.id, created_at=self.created_at, updated_at=self.updated_at)


class SellerModel(Base):
    __tablename__ = "sellers"

    id: Mapped[str] = mapped_column(String(128), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    nic_front: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    nic_rear: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> Seller:
        return Seller(
            id=self.id,
            nic_front=self.nic_front,
            nic_rear=self.nic_rear,
            is_verified=self.is_verified,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class MeasurementProfileModel(Base):
    __tablename__ = "measurement_profile"

    measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    chest: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    waist: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    shoulder: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleeve: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    neck: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hip: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inseam: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    length: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> MeasurementProfile:
        return MeasurementProfile(
            measurement_id=self.measurement_id,
            user_id=self.user_id,
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
