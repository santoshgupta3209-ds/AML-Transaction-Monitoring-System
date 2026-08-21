from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    customer_id: int,
    title: str,
    message: str
):
    """
    Create a notification for a customer.
    """

    notification = Notification(

        customer_id=customer_id,

        title=title,

        message=message,

        is_read=False
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def notify_suspicious_transaction(
    db: Session,
    customer_id: int,
    transaction_id: int
):
    """
    Notify customer that a transaction
    has been placed under review.
    """

    return create_notification(

        db=db,

        customer_id=customer_id,

        title="Transaction Under Review",

        message=(
            f"Transaction #{transaction_id} "
            "has been flagged for AML review."
        )
    )


def notify_transaction_completed(
    db: Session,
    customer_id: int,
    transaction_id: int
):
    """
    Notify customer that a transaction
    was completed.
    """

    return create_notification(

        db=db,

        customer_id=customer_id,

        title="Transaction Completed",

        message=(
            f"Transaction #{transaction_id} "
            "has been completed successfully."
        )
    )


def notify_account_frozen(
    db: Session,
    customer_id: int
):
    """Notify a customer that their account has been frozen."""

    return create_notification(
        db=db,
        customer_id=customer_id,
        title="Account Frozen",
        message="Your account is frozen. Please contact your bank.",
    )