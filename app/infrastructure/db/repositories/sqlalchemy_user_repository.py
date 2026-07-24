from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.user import User
from app.domain.repositories.user_repository import AbstractUserRepository
from app.infrastructure.db.models.user_model import UserModel


class SQLAlchemyUserRepository(AbstractUserRepository):
    """SQLAlchemy Async implementation of the AbstractUserRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        user_model = UserModel.from_domain(user)
        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)
        return user_model.to_domain()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        return [model.to_domain() for model in user_models]

    async def delete(self, user_id: int) -> bool:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        if user_model:
            await self.session.delete(user_model)
            await self.session.flush()
            return True
        return False
