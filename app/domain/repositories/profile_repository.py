from abc import ABC, abstractmethod

from app.domain.entities.user import Client, MeasurementProfile, Tailor


class AbstractClientRepository(ABC):
    """Contract for persisting Client profile records (Firebase UID as PK)."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: str) -> Client | None:
        pass


class AbstractTailorRepository(ABC):
    """Contract for persisting Tailor profile records (Firebase UID as PK). Maps to the 'tailors' table."""

    @abstractmethod
    async def create(self, tailor: Tailor) -> Tailor:
        pass

    @abstractmethod
    async def get_by_id(self, tailor_id: str) -> Tailor | None:
        pass

    @abstractmethod
    async def update_verification(self, tailor_id: str, is_verified: bool) -> Tailor:
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

