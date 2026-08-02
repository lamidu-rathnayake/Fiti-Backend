from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.shop import Shop, ShopImage
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.infrastructure.db.models.shop_model import ShopModel, ShopImageModel


class SQLAlchemyShopRepository(AbstractShopRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, shop: Shop) -> Shop:
        model = ShopModel(
            seller_id=shop.seller_id,
            shop_name=shop.shop_name,
            shop_bio=shop.shop_bio,
            shop_address=shop.shop_address,
            city=shop.city,
            contact_number=shop.contact_number,
            registration_number=shop.registration_number,
            latitude=shop.latitude,
            longitude=shop.longitude,
            average_rating=shop.average_rating,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        # Re-fetch with selectinload for relationship
        refetched = await self.get_by_id(model.shop_id)
        return refetched if refetched else model.to_domain()

    async def get_by_id(self, shop_id: int) -> Optional[Shop]:
        stmt = select(ShopModel).options(selectinload(ShopModel.images)).where(ShopModel.shop_id == shop_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_seller_id(self, seller_id: str) -> List[Shop]:
        stmt = (
            select(ShopModel)
            .options(selectinload(ShopModel.images))
            .where(ShopModel.seller_id == seller_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def list_all(self, skip: int = 0, limit: int = 100, city: Optional[str] = None) -> List[Shop]:
        stmt = select(ShopModel).options(selectinload(ShopModel.images))
        if city:
            stmt = stmt.where(ShopModel.city == city)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def add_image(self, image: ShopImage) -> ShopImage:
        model = ShopImageModel(shop_id=image.shop_id, image_url=image.image_url)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def update_average_rating(self, shop_id: int, new_rating: float) -> None:
        stmt = select(ShopModel).where(ShopModel.shop_id == shop_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.average_rating = new_rating
            await self.session.commit()
