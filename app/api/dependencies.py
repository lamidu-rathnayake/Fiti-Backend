from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.repositories.user_repository import AbstractUserRepository
from app.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.security.hashing import PasswordHasher
from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user import GetUserUseCase
from app.use_cases.user.list_users import ListUsersUseCase


# Repository Injection
def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> AbstractUserRepository:
    return SQLAlchemyUserRepository(session=session)


# Security Service Injection
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


# Use Case Injections
def get_create_user_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher),
) -> CreateUserUseCase:
    return CreateUserUseCase(user_repository=user_repo, password_hasher=hasher)


def get_user_by_id_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
) -> GetUserUseCase:
    return GetUserUseCase(user_repository=user_repo)


def get_list_users_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
) -> ListUsersUseCase:
    return ListUsersUseCase(user_repository=user_repo)
