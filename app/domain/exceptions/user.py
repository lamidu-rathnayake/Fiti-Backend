class DomainError(Exception):
    """Base exception for domain layer errors."""
    pass


class UserNotFoundError(DomainError):
    def __init__(self, identifier: str | int):
        self.identifier = identifier
        super().__init__(f"User with identifier '{identifier}' was not found.")


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")
