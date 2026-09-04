from app.domain.entities.shop import Gig, Shop, ShopImage
from app.domain.exceptions.shop import ShopNotFoundError
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.use_cases.dtos.shop_dto import (
    ShopCreateDTO,
    GigDTO,
    ShopImageDTO,
    ShopOutputDTO,
    ShopUpdateDTO,
)


class ManageShopUseCase:
    def __init__(self, shop_repository: AbstractShopRepository):
        self.shop_repository = shop_repository

    async def create_shop(self, dto: ShopCreateDTO) -> ShopOutputDTO:
        shop_entity = Shop(
            tailor_id=dto.tailor_id,
            shop_name=dto.shop_name,
            specialty=dto.specialty,
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

    async def get_shops_by_tailor(self, tailor_id: str) -> list[ShopOutputDTO]:
        shops = await self.shop_repository.get_by_tailor_id(tailor_id)
        return [self._to_dto(s) for s in shops]

    async def list_shops(
        self, skip: int = 0, limit: int = 100, city: str | None = None
    ) -> list[ShopOutputDTO]:
        shops = await self.shop_repository.list_all(skip=skip, limit=limit, city=city)
        return [self._to_dto(s) for s in shops]

    async def add_shop_image(self, shop_id: int, image_url: str) -> ShopImageDTO:
        shop = await self.shop_repository.get_by_id(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)
        img = ShopImage(shop_id=shop_id, image_url=image_url)
        saved = await self.shop_repository.add_image(img)
        return ShopImageDTO(
            image_id=saved.image_id, shop_id=saved.shop_id, image_url=saved.image_url
        )

    async def delete_shop_image(self, shop_id: int, image_id: int) -> bool:
        shop = await self.shop_repository.get_by_id(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)
        success = await self.shop_repository.delete_image(image_id)
        if not success:
            raise ValueError(f"Image {image_id} not found")
        return True

    async def update_shop(self, dto: ShopUpdateDTO) -> ShopOutputDTO:
        existing = await self.shop_repository.get_by_id(dto.shop_id)
        if not existing:
            raise ShopNotFoundError(dto.shop_id)
        shop_entity = Shop(
            shop_id=dto.shop_id,
            tailor_id=existing.tailor_id,
            shop_name=dto.shop_name,
            specialty=dto.specialty,
            shop_bio=dto.shop_bio,
            shop_address=dto.shop_address,
            city=dto.city,
            contact_number=dto.contact_number,
            registration_number=dto.registration_number,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
        updated = await self.shop_repository.update_shop(shop_entity)
        if not updated:
            raise ShopNotFoundError(dto.shop_id)
        return self._to_dto(updated)

    async def delete_shop(self, shop_id: int) -> bool:
        existing = await self.shop_repository.get_by_id(shop_id)
        if not existing:
            raise ShopNotFoundError(shop_id)
        return await self.shop_repository.delete_shop(shop_id)

    async def create_gig(self, shop_id: int, tailor_id: str, **data) -> GigDTO:
        shop = await self.shop_repository.get_by_id(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)
        if shop.tailor_id != tailor_id:
            raise PermissionError("You do not own this shop.")
        gig = await self.shop_repository.create_gig(Gig(shop_id=shop_id, **data))
        return self._gig_to_dto(gig)

    async def delete_gig(self, gig_id: int, tailor_id: str) -> bool:
        gig = await self.shop_repository.get_gig(gig_id)
        if not gig:
            raise ValueError(f"Gig {gig_id} not found")
        shop = await self.shop_repository.get_by_id(gig.shop_id)
        if not shop or shop.tailor_id != tailor_id:
            raise PermissionError("You do not own this shop.")
        return await self.shop_repository.delete_gig(gig_id)

    async def search_near_location(
        self, lat: float, lng: float, radius_km: float = 10.0
    ) -> list[ShopOutputDTO]:
        shops = await self.shop_repository.search_near_location(
            lat=lat, lng=lng, radius_km=radius_km
        )
        return [self._to_dto(s) for s in shops]

    def _to_dto(self, shop: Shop) -> ShopOutputDTO:
        return ShopOutputDTO(
            shop_id=shop.shop_id,  # type: ignore
            tailor_id=shop.tailor_id,
            shop_name=shop.shop_name,
            specialty=shop.specialty,
            shop_bio=shop.shop_bio,
            shop_address=shop.shop_address,
            city=shop.city,
            contact_number=shop.contact_number,
            registration_number=shop.registration_number,
            latitude=shop.latitude,
            longitude=shop.longitude,
            average_rating=shop.average_rating,
            images=[
                ShopImageDTO(
                    image_id=img.image_id, shop_id=img.shop_id, image_url=img.image_url
                )
                for img in shop.images
            ],
            gigs=[self._gig_to_dto(gig) for gig in shop.gigs],
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )

    def _gig_to_dto(self, gig: Gig) -> GigDTO:
        return GigDTO(
            gig_id=gig.gig_id,
            shop_id=gig.shop_id,
            title=gig.title,
            description=gig.description,
            price=gig.price,
            delivery_time=gig.delivery_time,
            category=gig.category,
            image_url=gig.image_url,
            created_at=gig.created_at,
            updated_at=gig.updated_at,
        )
