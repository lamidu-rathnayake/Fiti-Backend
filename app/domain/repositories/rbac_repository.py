from abc import ABC, abstractmethod

from app.domain.entities.rbac import Role


class AbstractRBACRepository(ABC):
    @abstractmethod
    async def get_role_by_name(self, name: str) -> Role | None:
        pass

    @abstractmethod
    async def assign_role_to_user(self, user_id: str, role_id: int) -> None:
        pass

    @abstractmethod
    async def get_user_roles(self, user_id: str) -> list[Role]:
        pass

