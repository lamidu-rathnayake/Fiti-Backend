from dataclasses import dataclass
from typing import Optional


@dataclass
class Role:
    id: Optional[int]
    name: str


@dataclass
class UserRole:
    user_id: str
    role_id: int


@dataclass
class Section:
    id: Optional[int]
    name: str
    route_name: str


@dataclass
class RoleSectionGrant:
    role_id: int
    section_id: int


@dataclass
class SubSection:
    id: Optional[int]
    name: str
    component_id: str


@dataclass
class SectionSubSection:
    section_id: int
    sub_section_id: int
