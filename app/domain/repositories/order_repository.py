from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.order import (
    ClothingRequest,
    ClothingRequestImage,
    Measurement,
    ShopRequest,
    Bid,
    Order,
    Payment,
    Rating,
)


class AbstractOrderRepository(ABC):
    @abstractmethod
    async def create_clothing_request(self, request: ClothingRequest) -> ClothingRequest:
        pass

    @abstractmethod
    async def get_clothing_request(self, request_id: int) -> Optional[ClothingRequest]:
        pass

    @abstractmethod
    async def list_clothing_requests_by_client(self, client_id: str) -> List[ClothingRequest]:
        pass

    @abstractmethod
    async def list_open_clothing_requests(self, skip: int = 0, limit: int = 100) -> List[ClothingRequest]:
        pass

    @abstractmethod
    async def add_design_image(self, image: ClothingRequestImage) -> ClothingRequestImage:
        pass

    @abstractmethod
    async def create_shop_request(self, shop_request: ShopRequest) -> ShopRequest:
        pass

    @abstractmethod
    async def get_shop_request(self, shop_request_id: int) -> Optional[ShopRequest]:
        pass

    @abstractmethod
    async def list_shop_requests_by_shop(self, shop_id: int) -> List[ShopRequest]:
        pass

    @abstractmethod
    async def create_bid(self, bid: Bid) -> Bid:
        pass

    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        pass

    @abstractmethod
    async def get_order(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    async def list_orders_by_shop(self, shop_id: int) -> List[Order]:
        pass

    @abstractmethod
    async def list_orders_by_client(self, client_id: str) -> List[Order]:
        pass

    @abstractmethod
    async def update_order_status(self, order_id: int, status: str) -> Order:
        pass

    @abstractmethod
    async def create_payment(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    async def create_rating(self, rating: Rating) -> Rating:
        pass
