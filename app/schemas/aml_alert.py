from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AMLAlertCreate(BaseModel):

    transaction_id: int

    risk_score: float

    risk_level: str

    alert_type: str | None = None

    description: str | None = None


class AMLAlertUpdate(BaseModel):

    status: str


class AMLAlertResponse(BaseModel):

    id: int

    transaction_id: int

    risk_score: float

    risk_level: str

    alert_type: str | None

    description: str | None

    status: str

    created_at: datetime

    resolved_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )