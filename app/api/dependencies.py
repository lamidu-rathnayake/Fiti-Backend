from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.repositories.user_repository import (
    AbstractUserRepository,
    AbstractClientRepository,
    AbstractSellerRepository,
    AbstractMeasurementProfileRepository,
)
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.domain.repositories.order_repository import AbstractOrderRepository
from app.domain.repositories.notification_repository import (
    AbstractNotificationRepository,
    AbstractFavoriteShopRepository,
)

from app.infrastructure.db.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
    SQLAlchemyClientRepository,
    SQLAlchemySellerRepository,
    SQLAlchemyMeasurementProfileRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_rbac_repository import SQLAlchemyRBACRepository
from app.infrastructure.db.repositories.sqlalchemy_shop_repository import SQLAlchemyShopRepository
from app.infrastructure.db.repositories.sqlalchemy_order_repository import SQLAlchemyOrderRepository
from app.infrastructure.db.repositories.sqlalchemy_support_repository import (
    SQLAlchemyNotificationRepository,
    SQLAlchemyFavoriteShopRepository,
)

from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user import GetUserUseCase
from app.use_cases.user.list_users import ListUsersUseCase
from app.use_cases.user.manage_measurement import ManageMeasurementProfileUseCase
from app.use_cases.rbac.manage_rbac import ManageRBACUseCase
from app.use_cases.shop.manage_shop import ManageShopUseCase
from app.use_cases.order.manage_order import ManageOrderUseCase


# Repositories
def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> AbstractUserRepository:
    return SQLAlchemyUserRepository(session=session)


def get_client_repository(session: AsyncSession = Depends(get_db_session)) -> AbstractClientRepository:
    return SQLAlchemyClientRepository(session=session)


def get_seller_repository(session: AsyncSession = Depends(get_db_session)) -> AbstractSellerRepository:
    return SQLAlchemySellerRepository(session=session)


def get_measurement_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractMeasurementProfileRepository:
    return SQLAlchemyMeasurementProfileRepository(session=session)


def get_rbac_repository(session: AsyncSession = Depends(get_db_session)) -> AbstractRBACRepository:
    return SQLAlchemyRBACRepository(session=session)


def get_shop_repository(session: AsyncSession = Depends(get_db_session)) -> AbstractShopRepository:
    return SQLAlchemyShopRepository(session=session)


def get_order_repository(session: AsyncSession = Depends(get_db_session)) -> AbstractOrderRepository:
    return SQLAlchemyOrderRepository(session=session)


# Use Cases
def get_create_user_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
    client_repo: AbstractClientRepository = Depends(get_client_repository),
    seller_repo: AbstractSellerRepository = Depends(get_seller_repository),
    rbac_repo: AbstractRBACRepository = Depends(get_rbac_repository),
) -> CreateUserUseCase:
    return CreateUserUseCase(
        user_repository=user_repo,
        client_repository=client_repo,
        seller_repository=seller_repo,
        rbac_repository=rbac_repo,
    )


def get_user_by_id_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
) -> GetUserUseCase:
    return GetUserUseCase(user_repository=user_repo)


def get_list_users_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
) -> ListUsersUseCase:
    return ListUsersUseCase(user_repository=user_repo)


def get_manage_measurement_use_case(
    meas_repo: AbstractMeasurementProfileRepository = Depends(get_measurement_repository),
) -> ManageMeasurementProfileUseCase:
    return ManageMeasurementProfileUseCase(profile_repository=meas_repo)


def get_manage_rbac_use_case(
    rbac_repo: AbstractRBACRepository = Depends(get_rbac_repository),
) -> ManageRBACUseCase:
    return ManageRBACUseCase(rbac_repository=rbac_repo)


def get_manage_shop_use_case(
    shop_repo: AbstractShopRepository = Depends(get_shop_repository),
) -> ManageShopUseCase:
    return ManageShopUseCase(shop_repository=shop_repo)


def get_manage_order_use_case(
    order_repo: AbstractOrderRepository = Depends(get_order_repository),
    shop_repo: AbstractShopRepository = Depends(get_shop_repository),
) -> ManageOrderUseCase:
    return ManageOrderUseCase(order_repository=order_repo, shop_repository=shop_repo)
