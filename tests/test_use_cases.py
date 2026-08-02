import pytest
from typing import Optional, List
from app.domain.entities.user import User, Client, Seller
from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.domain.repositories.user_repository import (
    AbstractUserRepository,
    AbstractClientRepository,
    AbstractSellerRepository,
)
from app.use_cases.dtos.user_dto import UserCreateInputDTO
from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user import GetUserUseCase


class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        self.users = {}

    async def create(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def update(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return list(self.users.values())[skip : skip + limit]

    async def delete(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


class InMemoryClientRepository(AbstractClientRepository):
    def __init__(self):
        self.clients = {}

    async def create(self, client: Client) -> Client:
        self.clients[client.id] = client
        return client

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        return self.clients.get(client_id)


class InMemorySellerRepository(AbstractSellerRepository):
    def __init__(self):
        self.sellers = {}

    async def create(self, seller: Seller) -> Seller:
        self.sellers[seller.id] = seller
        return seller

    async def get_by_id(self, seller_id: str) -> Optional[Seller]:
        return self.sellers.get(seller_id)

    async def update(self, seller: Seller) -> Seller:
        self.sellers[seller.id] = seller
        return seller


@pytest.mark.asyncio
async def test_create_user_use_case():
    repo = InMemoryUserRepository()
    client_repo = InMemoryClientRepository()
    seller_repo = InMemorySellerRepository()
    use_case = CreateUserUseCase(
        user_repository=repo, client_repository=client_repo, seller_repository=seller_repo
    )

    dto = UserCreateInputDTO(
        id="fb_uid_123", name="John Doe", email="test@example.com", auth_provider="email", role="client"
    )
    result = await use_case.execute(dto)

    assert result.id == "fb_uid_123"
    assert result.email == "test@example.com"
    assert result.name == "John Doe"
    assert "fb_uid_123" in client_repo.clients


@pytest.mark.asyncio
async def test_create_user_duplicate_id():
    repo = InMemoryUserRepository()
    client_repo = InMemoryClientRepository()
    seller_repo = InMemorySellerRepository()
    use_case = CreateUserUseCase(
        user_repository=repo, client_repository=client_repo, seller_repository=seller_repo
    )

    dto = UserCreateInputDTO(
        id="fb_uid_123", name="John Doe", email="test@example.com", auth_provider="email", role="client"
    )
    await use_case.execute(dto)

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_get_user_not_found():
    repo = InMemoryUserRepository()
    use_case = GetUserUseCase(user_repository=repo)

    with pytest.raises(UserNotFoundError):
        await use_case.execute("non_existent_uid")
