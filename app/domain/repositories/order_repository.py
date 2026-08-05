from abc import ABC, abstractmethod

from app.domain.entities.order import (
    Bid,
    ClothingRequest,
    ClothingRequestImage,
    Order,
    Payment,
    Rating,
    ShopRequest,
)


class AbstractOrderRepository(ABC):
    @abstractmethod
    async def create_clothing_request(self, request: ClothingRequest) -> ClothingRequest:
        pass

    @abstractmethod
    async def get_clothing_request(self, request_id: int) -> ClothingRequest | None:
        pass

    @abstractmethod
    async def list_clothing_requests_by_client(self, client_id: str) -> list[ClothingRequest]:
        pass

    @abstractmethod
    async def list_open_clothing_requests(self, skip: int = 0, limit: int = 100) -> list[ClothingRequest]:
        pass

    @abstractmethod
    async def add_design_image(self, image: ClothingRequestImage) -> ClothingRequestImage:
        pass

    @abstractmethod
    async def create_shop_request(self, shop_request: ShopRequest) -> ShopRequest:
        pass

    @abstractmethod
    async def get_shop_request(self, shop_request_id: int) -> ShopRequest | None:
        pass

    @abstractmethod
    async def list_shop_requests_by_shop(self, shop_id: int) -> list[ShopRequest]:
        pass

    @abstractmethod
    async def create_bid(self, bid: Bid) -> Bid:
        pass

    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        pass

    @abstractmethod
    async def get_order(self, order_id: int) -> Order | None:
        pass

    @abstractmethod
    async def list_orders_by_shop(self, shop_id: int) -> list[Order]:
        pass

    @abstractmethod
    async def list_orders_by_client(self, client_id: str) -> list[Order]:
        pass

    @abstractmethod
    async def update_order_status(self, order_id: int, status: str) -> Order:
        pass

    @abstractmethod
    async def create_payment(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    async def get_payment(self, payment_id: int) -> Payment | None:
        pass

    @abstractmethod
    async def create_rating(self, rating: Rating) -> Rating:
        pass

    @abstractmethod
    async def get_ratings_by_shop(self, shop_id: int) -> list[Rating]:
        pass
