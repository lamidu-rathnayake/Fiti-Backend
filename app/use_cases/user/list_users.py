from typing import List
from app.domain.repositories.user_repository import AbstractUserRepository
from app.use_cases.dtos.user_dto import UserOutputDTO


class ListUsersUseCase:
    """Application use case for listing all users."""

    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[UserOutputDTO]:
        users = await self.user_repository.list_all(skip=skip, limit=limit)
        return [
            UserOutputDTO(
                id=u.id,  # type: ignore
                email=u.email,
                username=u.username,
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at
            )
            for u in users
        ]
