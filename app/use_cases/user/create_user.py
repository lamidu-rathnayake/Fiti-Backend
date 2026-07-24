from app.domain.entities.user import User
from app.domain.exceptions.user import UserAlreadyExistsError
from app.domain.repositories.user_repository import AbstractUserRepository
from app.use_cases.dtos.user_dto import UserCreateInputDTO, UserOutputDTO


class CreateUserUseCase:
    """Application use case for registering a new user."""

    def __init__(self, user_repository: AbstractUserRepository, password_hasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, dto: UserCreateInputDTO) -> UserOutputDTO:
        existing_user = await self.user_repository.get_by_email(dto.email)
        if existing_user:
            raise UserAlreadyExistsError(email=dto.email)

        hashed_password = self.password_hasher.hash_password(dto.password)
        new_user = User(
            id=None,
            email=dto.email,
            username=dto.username,
            hashed_password=hashed_password,
            is_active=True
        )

        saved_user = await self.user_repository.create(new_user)
        return UserOutputDTO(
            id=saved_user.id,  # type: ignore
            email=saved_user.email,
            username=saved_user.username,
            is_active=saved_user.is_active,
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at
        )
