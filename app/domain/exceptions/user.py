class UserDomainException(Exception):
    """Base exception for user domain errors."""
    pass


class UserNotFoundError(UserDomainException):
    def __init__(self, user_id: str = None, identifier: str = None):
        uid = user_id or identifier
        super().__init__(f"User with ID '{uid}' not found.")


class UserAlreadyExistsError(UserDomainException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists.")


class ClientNotFoundError(UserDomainException):
    def __init__(self, client_id: str):
        super().__init__(f"Client profile with ID '{client_id}' not found.")


class SellerNotFoundError(UserDomainException):
    def __init__(self, seller_id: str):
        super().__init__(f"Seller profile with ID '{seller_id}' not found.")


class MeasurementProfileNotFoundError(UserDomainException):
    def __init__(self, user_id: str):
        super().__init__(f"Measurement profile for user '{user_id}' not found.")
