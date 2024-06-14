from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base_response import BaseResponse


class UserAuthSchema(BaseModel):
    email: str = Field(description="User unique email", examples=["user@celes.com"])
    password: str = Field(description="User strong password")


class AccessTokenSchema(BaseModel):
    token_id: str = Field(description="Authentication token ID")
    expires_in: str = Field(description="Token expiration time in seconds")


class AuthTokenResponseSchema(BaseResponse):
    data: Optional[AccessTokenSchema] = Field(
        description="JWT authentication token", default=None
    )
