from app.domain.exceptions.user import UserNotFoundError
from app.domain.repositories.user_repository import AbstractUserRepository
from app.use_cases.dtos.user_dto import UserOutputDTO


class GetUserUseCase:
    """Application use case for retrieving a user by ID."""

    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: int) -> UserOutputDTO:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(identifier=user_id)

        return UserOutputDTO(
            id=user.id,  # type: ignore
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
