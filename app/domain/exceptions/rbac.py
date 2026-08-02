class RBACDomainException(Exception):
    """Base exception for RBAC domain errors."""
    pass


class RoleNotFoundError(RBACDomainException):
    def __init__(self, role_id_or_name: str):
        super().__init__(f"Role '{role_id_or_name}' not found.")


class SectionNotFoundError(RBACDomainException):
    def __init__(self, section_id_or_name: str):
        super().__init__(f"Section '{section_id_or_name}' not found.")


class AccessDeniedError(RBACDomainException):
    def __init__(self, user_id: str, section_name: str):
        super().__init__(f"Access denied for user '{user_id}' to section '{section_name}'.")
