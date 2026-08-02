from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.shop import Shop, ShopImage


class AbstractShopRepository(ABC):
    @abstractmethod
    async def create(self, shop: Shop) -> Shop:
        pass

    @abstractmethod
    async def get_by_id(self, shop_id: int) -> Optional[Shop]:
        pass

    @abstractmethod
    async def get_by_seller_id(self, seller_id: str) -> List[Shop]:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100, city: Optional[str] = None) -> List[Shop]:
        pass

    @abstractmethod
    async def add_image(self, image: ShopImage) -> ShopImage:
        pass

    @abstractmethod
    async def update_average_rating(self, shop_id: int, new_rating: float) -> None:
        pass
