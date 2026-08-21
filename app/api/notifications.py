from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.notification import Notification
from app.models.customer import Customer

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# GET CUSTOMER NOTIFICATIONS
# ============================================================

@router.get("/customer/{customer_id}")
def get_notifications(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id
        )
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    notifications = (
        db.query(Notification)
        .filter(
            Notification.customer_id
            == customer_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return {
        "customer_id": customer_id,

        "notifications": [
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at
            }
            for notification in notifications
        ]
    }


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id
            == notification_id
        )
        .first()
    )

    if not notification:

        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message":
            "Notification marked as read"
    }