from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.rbac import (
    Role,
    UserRole,
)
from app.infrastructure.db.base import Base


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    def to_domain(self) -> Role:
        return Role(id=self.id, name=self.name)


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    # firebase_uid holds the Firebase Auth UID — no FK to a users table
    firebase_uid: Mapped[str] = mapped_column(String(128), primary_key=True)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    def to_domain(self) -> UserRole:
        return UserRole(user_id=self.firebase_uid, role_id=self.role_id)


