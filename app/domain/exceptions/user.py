class ProfileDomainException(Exception):
    """Base exception for profile domain errors."""


class ProfileNotFoundError(ProfileDomainException):
    def __init__(self, profile_id: str, role: str = "client"):
        super().__init__(f"{role.capitalize()} profile with Firebase UID '{profile_id}' not found.")


class ProfileAlreadyExistsError(ProfileDomainException):
    def __init__(self, profile_id: str, role: str = "client"):
        super().__init__(f"{role.capitalize()} profile for Firebase UID '{profile_id}' already exists.")


class ClientNotFoundError(ProfileDomainException):
    def __init__(self, client_id: str):
        super().__init__(f"Client profile with Firebase UID '{client_id}' not found.")


class TailorNotFoundError(ProfileDomainException):
    def __init__(self, tailor_id: str):
        super().__init__(f"Tailor profile with Firebase UID '{tailor_id}' not found.")


class MeasurementProfileNotFoundError(ProfileDomainException):
    def __init__(self, client_id: str):
        super().__init__(f"Measurement profile for client '{client_id}' not found.")

