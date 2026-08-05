from abc import ABC, abstractmethod

from app.domain.entities.shop import Shop, ShopImage


class AbstractShopRepository(ABC):
    @abstractmethod
    async def create(self, shop: Shop) -> Shop:
        pass

    @abstractmethod
    async def get_by_id(self, shop_id: int) -> Shop | None:
        pass

    @abstractmethod
    async def get_by_seller_id(self, seller_id: str) -> list[Shop]:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100, city: str | None = None) -> list[Shop]:
        pass

    @abstractmethod
    async def add_image(self, image: ShopImage) -> ShopImage:
        pass

    @abstractmethod
    async def update_average_rating(self, shop_id: int, new_rating: float) -> None:
        pass
        
    @abstractmethod
    async def update_shop(self, shop: Shop) -> Shop | None:
        """Update shop details (bio, address, contact number)."""

    @abstractmethod
    async def delete_shop(self, shop_id: int) -> bool:
        """Soft-delete or remove a shop."""

    @abstractmethod
    async def search_near_location(self, lat: float, lng: float, radius_km: float = 10.0) -> list[Shop]:
        """Find tailor shops within a GPS radius."""
