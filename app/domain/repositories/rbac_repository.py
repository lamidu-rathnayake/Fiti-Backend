from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.rbac import Role, Section, SubSection


class AbstractRBACRepository(ABC):
    @abstractmethod
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        pass

    @abstractmethod
    async def assign_role_to_user(self, user_id: str, role_id: int) -> None:
        pass

    @abstractmethod
    async def get_user_roles(self, user_id: str) -> List[Role]:
        pass

    @abstractmethod
    async def get_accessible_sections_for_user(self, user_id: str) -> List[Section]:
        pass

    @abstractmethod
    async def check_user_access_to_route(self, user_id: str, route_name: str) -> bool:
        pass
