from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):

    user_id: int

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )


class CustomerUpdate(BaseModel):

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    status: str | None = None


class AdminCustomerCreate(BaseModel):

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

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    account_number: str = Field(
        ...,
        min_length=8,
        max_length=30
    )

    account_type: str = Field(
        default="SAVINGS"
    )

    balance: Decimal = Field(
        default=0,
        ge=0
    )

    status: str = Field(
        default="ACTIVE"
    )


class AdminCustomerUpdate(BaseModel):

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=100
    )

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    account_number: str | None = Field(
        default=None,
        min_length=8,
        max_length=30
    )

    account_type: str | None = None

    balance: Decimal | None = Field(
        default=None,
        ge=0
    )

    status: str | None = None


class CustomerResponse(BaseModel):

    id: int

    user_id: int

    full_name: str

    phone: str | None

    address: str | None

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )