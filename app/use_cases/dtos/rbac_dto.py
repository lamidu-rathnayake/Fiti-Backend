from dataclasses import dataclass
from typing import List


@dataclass
class RoleAssignDTO:
    user_id: str
    role_name: str


@dataclass
class SectionOutputDTO:
    id: int
    name: str
    route_name: str


@dataclass
class UserAccessOverviewDTO:
    user_id: str
    roles: List[str]
    accessible_sections: List[SectionOutputDTO]
