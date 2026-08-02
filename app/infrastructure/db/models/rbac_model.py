from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.entities.rbac import Role, Section, SubSection


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
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)


class SectionModel(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    route_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def to_domain(self) -> Section:
        return Section(id=self.id, name=self.name, route_name=self.route_name)


class RoleSectionGrantModel(Base):
    __tablename__ = "role_section_grants"

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), primary_key=True)


class SubSectionModel(Base):
    __tablename__ = "sub_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    component_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def to_domain(self) -> SubSection:
        return SubSection(id=self.id, name=self.name, component_id=self.component_id)


