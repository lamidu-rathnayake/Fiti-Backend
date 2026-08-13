from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.support import FavoriteShop, Notification
from app.domain.repositories.notification_repository import (
    AbstractFavoriteShopRepository,
    AbstractNotificationRepository,
)
from app.infrastructure.db.models.support_model import (
    FavoriteShopModel,
    NotificationModel,
)


class SQLAlchemyNotificationRepository(AbstractNotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(self, notification: Notification) -> Notification:
        model = NotificationModel(
            firebase_uid=notification.user_id,
            title=notification.title,
            message=notification.message,
            is_read=notification.is_read,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def list_by_user(self, user_id: str) -> list[Notification]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.firebase_uid == user_id)
            .order_by(NotificationModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def mark_read(self, notification_id: int) -> bool:
        stmt = select(NotificationModel).where(
            NotificationModel.notification_id == notification_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.is_read = True
            await self.session.commit()
            return True
        return False


class SQLAlchemyFavoriteShopRepository(AbstractFavoriteShopRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_favorite(self, favorite: FavoriteShop) -> FavoriteShop:
        model = FavoriteShopModel(
            client_id=favorite.client_id, shop_id=favorite.shop_id
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def remove_favorite(self, client_id: str, shop_id: int) -> bool:
        stmt = select(FavoriteShopModel).where(
            FavoriteShopModel.client_id == client_id,
            FavoriteShopModel.shop_id == shop_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False

    async def list_favorites_by_client(self, client_id: str) -> list[FavoriteShop]:
        stmt = select(FavoriteShopModel).where(FavoriteShopModel.client_id == client_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]
