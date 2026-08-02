from typing import List, Optional
from app.domain.entities.shop import Shop, ShopImage
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.domain.exceptions.shop import ShopNotFoundError
from app.use_cases.dtos.shop_dto import ShopCreateDTO, ShopOutputDTO, ShopImageDTO


class ManageShopUseCase:
    def __init__(self, shop_repository: AbstractShopRepository):
        self.shop_repository = shop_repository

    async def create_shop(self, dto: ShopCreateDTO) -> ShopOutputDTO:
        shop_entity = Shop(
            seller_id=dto.seller_id,
            shop_name=dto.shop_name,
            shop_bio=dto.shop_bio,
            shop_address=dto.shop_address,
            city=dto.city,
            contact_number=dto.contact_number,
            registration_number=dto.registration_number,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
        saved = await self.shop_repository.create(shop_entity)
        return self._to_dto(saved)

    async def get_shop_by_id(self, shop_id: int) -> ShopOutputDTO:
        shop = await self.shop_repository.get_by_id(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)
        return self._to_dto(shop)

    async def get_shops_by_seller(self, seller_id: str) -> List[ShopOutputDTO]:
        shops = await self.shop_repository.get_by_seller_id(seller_id)
        return [self._to_dto(s) for s in shops]

    async def list_shops(self, skip: int = 0, limit: int = 100, city: Optional[str] = None) -> List[ShopOutputDTO]:
        shops = await self.shop_repository.list_all(skip=skip, limit=limit, city=city)
        return [self._to_dto(s) for s in shops]

    async def add_shop_image(self, shop_id: int, image_url: str) -> ShopImageDTO:
        shop = await self.shop_repository.get_by_id(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)
        img = ShopImage(shop_id=shop_id, image_url=image_url)
        saved = await self.shop_repository.add_image(img)
        return ShopImageDTO(image_id=saved.image_id, shop_id=saved.shop_id, image_url=saved.image_url)

    def _to_dto(self, shop: Shop) -> ShopOutputDTO:
        return ShopOutputDTO(
            shop_id=shop.shop_id,  # type: ignore
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
            images=[
                ShopImageDTO(image_id=img.image_id, shop_id=img.shop_id, image_url=img.image_url)
                for img in shop.images
            ],
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )
