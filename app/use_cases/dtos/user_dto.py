from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserCreateInputDTO:
    email: str
    username: str
    password: str


@dataclass(frozen=True)
class UserOutputDTO:
    id: int
    email: str
    username: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
