from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )

    role: Literal["CUSTOMER", "ADMIN"] = "CUSTOMER"


class LoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user_id: int

    username: str

    role: str