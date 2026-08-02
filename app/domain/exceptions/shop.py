class ShopDomainException(Exception):
    """Base exception for Shop domain errors."""
    pass


class ShopNotFoundError(ShopDomainException):
    def __init__(self, shop_id: int):
        super().__init__(f"Shop with ID '{shop_id}' not found.")
