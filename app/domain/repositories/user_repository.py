from abc import ABC, abstractmethod
from typing import Sequence, Optional
from app.domain.entities.user import User


class AbstractUserRepository(ABC):
    """Abstract Repository Interface for User Domain Entity."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persists a new User entity."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieves a User domain entity by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a User domain entity by email."""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Lists User domain entities with pagination."""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Deletes a User entity by ID."""
        pass
