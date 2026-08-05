
from pydantic import BaseModel, Field


class RoleAssignRequest(BaseModel):
    user_id: str = Field(..., description="Firebase Auth UID of the user")
    role_name: str = Field(..., description="Name of the role to assign (e.g. 'client', 'seller', 'admin')")


class SectionResponse(BaseModel):
    id: int
    name: str
    route_name: str


class UserAccessOverviewResponse(BaseModel):
    user_id: str
    roles: list[str]
    accessible_sections: list[SectionResponse]
