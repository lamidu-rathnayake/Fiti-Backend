from typing import List
from app.domain.repositories.user_repository import AbstractUserRepository
from app.use_cases.dtos.user_dto import UserOutputDTO


class ListUsersUseCase:
    """Application use case for listing users."""

    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[UserOutputDTO]:
        users = await self.user_repository.list_all(skip=skip, limit=limit)
        return [
            UserOutputDTO(
                id=u.id,
                name=u.name,
                email=u.email,
                auth_provider=u.auth_provider,
                whatsapp_number=u.whatsapp_number,
                address=u.address,
                city=u.city,
                postal_code=u.postal_code,
                gender=u.gender,
                age=u.age,
                profile_image=u.profile_image,
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]
