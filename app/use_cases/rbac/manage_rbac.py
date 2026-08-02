from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.domain.exceptions.rbac import RoleNotFoundError, AccessDeniedError
from app.use_cases.dtos.rbac_dto import RoleAssignDTO, UserAccessOverviewDTO, SectionOutputDTO


class ManageRBACUseCase:
    def __init__(self, rbac_repository: AbstractRBACRepository):
        self.rbac_repository = rbac_repository

    async def assign_role(self, dto: RoleAssignDTO) -> None:
        role = await self.rbac_repository.get_role_by_name(dto.role_name)
        if not role or role.id is None:
            raise RoleNotFoundError(dto.role_name)
        await self.rbac_repository.assign_role_to_user(dto.user_id, role.id)

    async def get_user_access_overview(self, user_id: str) -> UserAccessOverviewDTO:
        roles = await self.rbac_repository.get_user_roles(user_id)
        sections = await self.rbac_repository.get_accessible_sections_for_user(user_id)
        return UserAccessOverviewDTO(
            user_id=user_id,
            roles=[r.name for r in roles],
            accessible_sections=[
                SectionOutputDTO(id=s.id, name=s.name, route_name=s.route_name)
                for s in sections
                if s.id is not None
            ],
        )

    async def verify_user_route_access(self, user_id: str, route_name: str) -> bool:
        has_access = await self.rbac_repository.check_user_access_to_route(user_id, route_name)
        if not has_access:
            raise AccessDeniedError(user_id=user_id, section_route=route_name)
        return True
