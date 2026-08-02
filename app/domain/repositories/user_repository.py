from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User, Client, Seller, MeasurementProfile


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        pass


class AbstractClientRepository(ABC):
    @abstractmethod
    async def create(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        pass


class AbstractSellerRepository(ABC):
    @abstractmethod
    async def create(self, seller: Seller) -> Seller:
        pass

    @abstractmethod
    async def get_by_id(self, seller_id: str) -> Optional[Seller]:
        pass

    @abstractmethod
    async def update(self, seller: Seller) -> Seller:
        pass


class AbstractMeasurementProfileRepository(ABC):
    @abstractmethod
    async def upsert(self, profile: MeasurementProfile) -> MeasurementProfile:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[MeasurementProfile]:
        pass
