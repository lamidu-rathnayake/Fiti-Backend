from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Pure Domain Entity representing a User in the business logic layer."""
    id: Optional[int]
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def deactivate(self) -> None:
        """Example domain behavior method."""
        self.is_active = False
