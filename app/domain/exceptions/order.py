class OrderDomainException(Exception):
    """Base exception for Order domain errors."""


class ClothingRequestNotFoundError(OrderDomainException):
    def __init__(self, request_id: int):
        super().__init__(f"Clothing request with ID '{request_id}' not found.")


class ShopRequestNotFoundError(OrderDomainException):
    def __init__(self, shop_request_id: int):
        super().__init__(f"Shop request with ID '{shop_request_id}' not found.")


class OrderNotFoundError(OrderDomainException):
    def __init__(self, order_id: int):
        super().__init__(f"Order with ID '{order_id}' not found.")


class InvalidOrderStateError(OrderDomainException):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidOrderStateTransitionError(OrderDomainException):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            f"Cannot transition order from '{current_status}' to '{target_status}'."
        )
