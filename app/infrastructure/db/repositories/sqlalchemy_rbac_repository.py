from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.rbac import Role, Section
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.infrastructure.db.models.rbac_model import (
    RoleModel,
    UserRoleModel,
)


class SQLAlchemyRBACRepository(AbstractRBACRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_role_by_name(self, name: str) -> Role | None:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def assign_role_to_user(self, user_id: str, role_id: int) -> None:
        stmt = select(UserRoleModel).where(
            UserRoleModel.firebase_uid == user_id, UserRoleModel.role_id == role_id
        )
        res = await self.session.execute(stmt)
        if not res.scalar_one_or_none():
            ur = UserRoleModel(firebase_uid=user_id, role_id=role_id)
            self.session.add(ur)
            await self.session.flush()

    async def get_user_roles(self, user_id: str) -> list[Role]:
        stmt = (
            select(RoleModel)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
            .where(UserRoleModel.firebase_uid == user_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

