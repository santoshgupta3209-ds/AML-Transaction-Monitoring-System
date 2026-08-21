from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):

    customer_id: int

    account_number: str = Field(
        ...,
        min_length=8,
        max_length=30
    )

    account_type: str = "SAVINGS"

    balance: Decimal = Field(
        default=0,
        ge=0
    )


class AccountUpdate(BaseModel):

    account_type: str | None = None

    status: str | None = None


class AccountResponse(BaseModel):

    id: int

    customer_id: int

    account_number: str

    account_type: str

    balance: Decimal

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )