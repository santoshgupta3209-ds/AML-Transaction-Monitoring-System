from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):

    customer_id: int

    title: str

    message: str


class NotificationResponse(BaseModel):

    id: int

    customer_id: int

    title: str

    message: str

    is_read: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )