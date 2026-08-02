import pytest
from app.domain.entities.user import Client, Seller
from app.domain.exceptions.user import ProfileAlreadyExistsError
from app.use_cases.dtos.user_dto import ClientRegisterDTO, SellerRegisterDTO
from app.use_cases.user.manage_profile import ManageProfileUseCase
from app.domain.repositories.profile_repository import (
    AbstractClientRepository,
    AbstractSellerRepository,
    AbstractMeasurementProfileRepository,
)
from typing import Optional, Dict


class InMemoryClientRepository(AbstractClientRepository):
    def __init__(self):
        self._store: Dict[str, Client] = {}

    async def create(self, client: Client) -> Client:
        self._store[client.id] = client
        return client

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        return self._store.get(client_id)


class InMemorySellerRepository(AbstractSellerRepository):
    def __init__(self):
        self._store: Dict[str, Seller] = {}

    async def create(self, seller: Seller) -> Seller:
        self._store[seller.id] = seller
        return seller

    async def get_by_id(self, seller_id: str) -> Optional[Seller]:
        return self._store.get(seller_id)

    async def update_verification(self, seller_id: str, is_verified: bool) -> Seller:
        seller = self._store[seller_id]
        seller.is_verified = is_verified
        return seller


class InMemoryMeasurementRepository(AbstractMeasurementProfileRepository):
    def __init__(self):
        self._store = {}

    async def create(self, profile):
        self._store[profile.client_id] = profile
        return profile

    async def get_by_client_id(self, client_id: str):
        return self._store.get(client_id)

    async def update(self, profile):
        self._store[profile.client_id] = profile
        return profile


def make_use_case():
    return ManageProfileUseCase(
        client_repository=InMemoryClientRepository(),
        seller_repository=InMemorySellerRepository(),
        measurement_repository=InMemoryMeasurementRepository(),
    )


@pytest.mark.asyncio
async def test_register_client_profile():
    use_case = make_use_case()
    result = await use_case.register_client(ClientRegisterDTO(id="firebase_uid_abc"))
    assert result.id == "firebase_uid_abc"


@pytest.mark.asyncio
async def test_register_client_duplicate_raises_error():
    use_case = make_use_case()
    await use_case.register_client(ClientRegisterDTO(id="firebase_uid_abc"))
    with pytest.raises(ProfileAlreadyExistsError):
        await use_case.register_client(ClientRegisterDTO(id="firebase_uid_abc"))


@pytest.mark.asyncio
async def test_register_seller_profile():
    use_case = make_use_case()
    result = await use_case.register_seller(
        SellerRegisterDTO(
            id="seller_fb_001",
            nic_front="https://storage.googleapis.com/fiti/nic/front.jpg",
        )
    )
    assert result.id == "seller_fb_001"
    assert result.is_verified is False
    assert result.nic_front == "https://storage.googleapis.com/fiti/nic/front.jpg"
