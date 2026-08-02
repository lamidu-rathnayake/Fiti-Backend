from typing import Optional
from app.domain.entities.user import User, Client, Seller
from app.domain.exceptions.user import UserAlreadyExistsError
from app.domain.repositories.user_repository import (
    AbstractUserRepository,
    AbstractClientRepository,
    AbstractSellerRepository,
)
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.use_cases.dtos.user_dto import UserCreateInputDTO, UserOutputDTO


class CreateUserUseCase:
    """Application use case for registering/synchronizing a Firebase Auth user."""

    def __init__(
        self,
        user_repository: AbstractUserRepository,
        client_repository: AbstractClientRepository,
        seller_repository: AbstractSellerRepository,
        rbac_repository: Optional[AbstractRBACRepository] = None,
    ):
        self.user_repository = user_repository
        self.client_repository = client_repository
        self.seller_repository = seller_repository
        self.rbac_repository = rbac_repository

    async def execute(self, dto: UserCreateInputDTO) -> UserOutputDTO:
        existing_user = await self.user_repository.get_by_id(dto.id)
        if existing_user:
            raise UserAlreadyExistsError(email=dto.email)

        new_user = User(
            id=dto.id,
            name=dto.name,
            email=dto.email,
            auth_provider=dto.auth_provider,
            whatsapp_number=dto.whatsapp_number,
            address=dto.address,
            city=dto.city,
            postal_code=dto.postal_code,
            gender=dto.gender,
            age=dto.age,
            profile_image=dto.profile_image,
            is_active=True,
        )

        saved_user = await self.user_repository.create(new_user)

        # Create Client or Seller profile based on role
        if dto.role.lower() == "seller":
            seller = Seller(id=saved_user.id)
            await self.seller_repository.create(seller)
            if self.rbac_repository:
                role = await self.rbac_repository.get_role_by_name("seller")
                if role and role.id is not None:
                    await self.rbac_repository.assign_role_to_user(saved_user.id, role.id)
        else:
            client = Client(id=saved_user.id)
            await self.client_repository.create(client)
            if self.rbac_repository:
                role = await self.rbac_repository.get_role_by_name("client")
                if role and role.id is not None:
                    await self.rbac_repository.assign_role_to_user(saved_user.id, role.id)

        return UserOutputDTO(
            id=saved_user.id,
            name=saved_user.name,
            email=saved_user.email,
            auth_provider=saved_user.auth_provider,
            whatsapp_number=saved_user.whatsapp_number,
            address=saved_user.address,
            city=saved_user.city,
            postal_code=saved_user.postal_code,
            gender=saved_user.gender,
            age=saved_user.age,
            profile_image=saved_user.profile_image,
            is_active=saved_user.is_active,
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
        )
