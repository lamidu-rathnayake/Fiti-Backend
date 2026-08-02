from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.repositories.profile_repository import (
    AbstractClientRepository,
    AbstractSellerRepository,
    AbstractMeasurementProfileRepository,
)
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.domain.repositories.order_repository import AbstractOrderRepository

from app.infrastructure.db.repositories.sqlalchemy_profile_repository import (
    SQLAlchemyClientRepository,
    SQLAlchemySellerRepository,
    SQLAlchemyMeasurementProfileRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_rbac_repository import SQLAlchemyRBACRepository
from app.infrastructure.db.repositories.sqlalchemy_shop_repository import SQLAlchemyShopRepository
from app.infrastructure.db.repositories.sqlalchemy_order_repository import SQLAlchemyOrderRepository

from app.use_cases.user.manage_profile import ManageProfileUseCase
from app.use_cases.rbac.manage_rbac import ManageRBACUseCase
from app.use_cases.shop.manage_shop import ManageShopUseCase
from app.use_cases.order.manage_order import ManageOrderUseCase


# ── Repository Factories ──────────────────────────────────────────────────────

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


# ── Use Case Factories ────────────────────────────────────────────────────────

def get_manage_profile_use_case(
    client_repo: AbstractClientRepository = Depends(get_client_repository),
    seller_repo: AbstractSellerRepository = Depends(get_seller_repository),
    meas_repo: AbstractMeasurementProfileRepository = Depends(get_measurement_repository),
) -> ManageProfileUseCase:
    return ManageProfileUseCase(
        client_repository=client_repo,
        seller_repository=seller_repo,
        measurement_repository=meas_repo,
    )


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
