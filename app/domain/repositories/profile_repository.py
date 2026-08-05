from abc import ABC, abstractmethod

from app.domain.entities.user import Client, MeasurementProfile, Seller


class AbstractClientRepository(ABC):
    """Contract for persisting Client profile records (Firebase UID as PK)."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: str) -> Client | None:
        pass


class AbstractSellerRepository(ABC):
    """Contract for persisting Seller profile records (Firebase UID as PK)."""

    @abstractmethod
    async def create(self, seller: Seller) -> Seller:
        pass

    @abstractmethod
    async def get_by_id(self, seller_id: str) -> Seller | None:
        pass

    @abstractmethod
    async def update_verification(self, seller_id: str, is_verified: bool) -> Seller:
        pass


class AbstractMeasurementProfileRepository(ABC):
    """Contract for persisting client standard measurement profiles."""

    @abstractmethod
    async def create(self, profile: MeasurementProfile) -> MeasurementProfile:
        pass

    @abstractmethod
    async def get_by_client_id(self, client_id: str) -> MeasurementProfile | None:
        pass

    @abstractmethod
    async def update(self, profile: MeasurementProfile) -> MeasurementProfile:
        pass
