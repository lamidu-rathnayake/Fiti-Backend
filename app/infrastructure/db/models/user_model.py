from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.entities.user import User


class UserModel(Base):
    """SQLAlchemy ORM Model for users table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
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
        """Converts ORM model to pure Domain entity."""
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        """Creates ORM model from pure Domain entity."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )
