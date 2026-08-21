from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


# ============================================================
# CREATE TRANSACTION
# ============================================================

class TransactionCreate(BaseModel):

    sender_account: str = Field(
        ...,
        min_length=8,
        max_length=30
    )

    receiver_account: str = Field(
        ...,
        min_length=8,
        max_length=30
    )

    amount: Decimal = Field(
        ...,
        gt=0
    )

    transaction_type: str = Field(
        ...,
        max_length=50
    )

    transaction_channel: str = Field(
        ...,
        max_length=50
    )

    transaction_location: str | None = Field(
        default=None,
        max_length=100
    )

    # ========================================================
    # ML FEATURES
    # ========================================================

    transaction_hour: int = Field(
        ...,
        ge=0,
        le=23
    )

    transaction_frequency: int = Field(
        ...,
        ge=0
    )

    average_transaction_amount: float = Field(
        ...,
        ge=0
    )

    account_age_days: int = Field(
        ...,
        ge=0
    )

    previous_transaction_count: int = Field(
        ...,
        ge=0
    )

    previous_suspicious_count: int = Field(
        ...,
        ge=0
    )

    receiver_count: int = Field(
        ...,
        ge=0
    )

    international_transaction: int = Field(
        ...,
        ge=0,
        le=1
    )

    cash_transaction: int = Field(
        ...,
        ge=0,
        le=1
    )


# ============================================================
# TRANSACTION RESPONSE
# ============================================================

class TransactionResponse(BaseModel):

    id: int

    sender_account_id: int

    receiver_account_id: int

    amount: Decimal

    transaction_type: str

    transaction_channel: str

    transaction_location: str | None

    risk_probability: float | None

    risk_level: str | None

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )