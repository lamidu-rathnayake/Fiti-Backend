from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "user@example.com"})
    username: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "johndoe"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secretpassword123"})


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
