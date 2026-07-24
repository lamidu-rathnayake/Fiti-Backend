import pytest
from app.domain.entities.user import User
from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from app.domain.repositories.user_repository import AbstractUserRepository
from app.use_cases.dtos.user_dto import UserCreateInputDTO
from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user import GetUserUseCase


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory mock repository for domain unit testing without DB."""

    def __init__(self):
        self.users = {}
        self._id_counter = 1

    async def create(self, user: User) -> User:
        user.id = self._id_counter
        self._id_counter += 1
        self.users[user.id] = user
        return user

    async def get_by_id(self, user_id: int):
        return self.users.get(user_id)

    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def list_all(self, skip: int = 0, limit: int = 100):
        return list(self.users.values())[skip : skip + limit]

    async def delete(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


class DummyHasher:
    def hash_password(self, pwd: str) -> str:
        return f"hashed_{pwd}"


@pytest.mark.asyncio
async def test_create_user_use_case():
    repo = InMemoryUserRepository()
    hasher = DummyHasher()
    use_case = CreateUserUseCase(user_repository=repo, password_hasher=hasher)

    dto = UserCreateInputDTO(email="test@example.com", username="testuser", password="password123")
    result = await use_case.execute(dto)

    assert result.id == 1
    assert result.email == "test@example.com"
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    repo = InMemoryUserRepository()
    hasher = DummyHasher()
    use_case = CreateUserUseCase(user_repository=repo, password_hasher=hasher)

    dto = UserCreateInputDTO(email="test@example.com", username="testuser", password="password123")
    await use_case.execute(dto)

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_get_user_not_found():
    repo = InMemoryUserRepository()
    use_case = GetUserUseCase(user_repository=repo)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(999)
