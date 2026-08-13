from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.repositories.notification_repository import (
    AbstractFavoriteShopRepository,
    AbstractNotificationRepository,
)
from app.domain.repositories.order_repository import AbstractOrderRepository
from app.domain.repositories.profile_repository import (
    AbstractClientRepository,
    AbstractMeasurementProfileRepository,
    AbstractTailorRepository,
)
from app.domain.repositories.rbac_repository import AbstractRBACRepository
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.infrastructure.db.repositories.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_profile_repository import (
    SQLAlchemyClientRepository,
    SQLAlchemyMeasurementProfileRepository,
    SQLAlchemyTailorRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_rbac_repository import (
    SQLAlchemyRBACRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_shop_repository import (
    SQLAlchemyShopRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_support_repository import (
    SQLAlchemyFavoriteShopRepository,
    SQLAlchemyNotificationRepository,
)
from app.use_cases.order.manage_order import ManageOrderUseCase
from app.use_cases.rbac.manage_rbac import ManageRBACUseCase
from app.use_cases.shop.manage_shop import ManageShopUseCase
from app.use_cases.support.manage_support import ManageSupportUseCase
from app.use_cases.user.manage_profile import ManageProfileUseCase

# ── Repository Factories ──────────────────────────────────────────────────────


def get_client_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractClientRepository:
    return SQLAlchemyClientRepository(session=session)


def get_tailor_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractTailorRepository:
    return SQLAlchemyTailorRepository(session=session)


def get_measurement_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractMeasurementProfileRepository:
    return SQLAlchemyMeasurementProfileRepository(session=session)


def get_rbac_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractRBACRepository:
    return SQLAlchemyRBACRepository(session=session)


def get_shop_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractShopRepository:
    return SQLAlchemyShopRepository(session=session)


def get_order_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractOrderRepository:
    return SQLAlchemyOrderRepository(session=session)


def get_notification_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractNotificationRepository:
    return SQLAlchemyNotificationRepository(session=session)


def get_favorite_shop_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractFavoriteShopRepository:
    return SQLAlchemyFavoriteShopRepository(session=session)


# ── Use Case Factories ────────────────────────────────────────────────────────


def get_manage_profile_use_case(
    client_repo: AbstractClientRepository = Depends(get_client_repository),
    tailor_repo: AbstractTailorRepository = Depends(get_tailor_repository),
    meas_repo: AbstractMeasurementProfileRepository = Depends(
        get_measurement_repository
    ),
) -> ManageProfileUseCase:
    return ManageProfileUseCase(
        client_repository=client_repo,
        tailor_repository=tailor_repo,
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


def get_manage_support_use_case(
    notification_repo: AbstractNotificationRepository = Depends(
        get_notification_repository
    ),
    favorite_shop_repo: AbstractFavoriteShopRepository = Depends(
        get_favorite_shop_repository
    ),
) -> ManageSupportUseCase:
    return ManageSupportUseCase(
        notification_repository=notification_repo,
        favorite_shop_repository=favorite_shop_repo,
    )
