from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.rbac import (
    Role,
    RoleSectionGrant,
    Section,
    SectionSubSection,
    SubSection,
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
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    def to_domain(self) -> UserRole:
        return UserRole(user_id=self.firebase_uid, role_id=self.role_id)


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

    def to_domain(self) -> RoleSectionGrant:
        return RoleSectionGrant(role_id=self.role_id, section_id=self.section_id)


class SubSectionModel(Base):
    """Sub-section component. Linked to sections via the section_sub_sections junction table."""
    __tablename__ = "sub_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def to_domain(self) -> SubSection:
        return SubSection(id=self.id, section_id=0, name=self.name, component_id=self.component_id)


class SectionSubSectionModel(Base):
    """Junction table linking sections to sub-sections (many-to-many)."""
    __tablename__ = "section_sub_sections"

    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), primary_key=True)
    sub_section_id: Mapped[int] = mapped_column(Integer, ForeignKey("sub_sections.id", ondelete="CASCADE"), primary_key=True)

    def to_domain(self) -> SectionSubSection:
        return SectionSubSection(section_id=self.section_id, sub_section_id=self.sub_section_id)
