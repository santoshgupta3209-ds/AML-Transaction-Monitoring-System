from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction

from app.services.aml_service import (
    process_aml_check
)

from app.services.notification_service import (
    notify_suspicious_transaction,
    notify_transaction_completed
)


def get_account_by_number(
    db: Session,
    account_number: str
):
    """
    Find an account by account number.
    """

    return (
        db.query(Account)
        .filter(
            Account.account_number
            == account_number
        )
        .first()
    )


def validate_transaction(
    sender: Account,
    receiver: Account,
    amount: float
):
    """
    Validate transaction before processing.
    """

    if sender is None:
        raise ValueError(
            "Sender account not found"
        )

    if receiver is None:
        raise ValueError(
            "Receiver account not found"
        )

    if sender.id == receiver.id:
        raise ValueError(
            "Sender and receiver cannot be same"
        )

    if sender.status != "ACTIVE":
        raise ValueError(
            "Sender account is not active"
        )

    if receiver.status != "ACTIVE":
        raise ValueError(
            "Receiver account is not active"
        )

    if amount <= 0:
        raise ValueError(
            "Transaction amount must be greater than zero"
        )

    if float(sender.balance) < amount:
        raise ValueError(
            "Insufficient balance"
        )


def create_transaction(
    db: Session,
    sender_account_number: str,
    receiver_account_number: str,
    amount: float,
    transaction_type: str,
    transaction_channel: str,
    transaction_location: str,
    ml_data: dict
):
    """
    Create and process a transaction.
    """

    # --------------------------------------------------------
    # Find accounts
    # --------------------------------------------------------

    sender = get_account_by_number(
        db,
        sender_account_number
    )

    receiver = get_account_by_number(
        db,
        receiver_account_number
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_transaction(
        sender,
        receiver,
        amount
    )

    # --------------------------------------------------------
    # Create transaction
    # --------------------------------------------------------

    transaction = Transaction(

        sender_account_id=sender.id,

        receiver_account_id=receiver.id,

        amount=amount,

        transaction_type=transaction_type,

        transaction_channel=transaction_channel,

        transaction_location=transaction_location,

        status="PENDING"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # --------------------------------------------------------
    # AML prediction
    # --------------------------------------------------------

    result = process_aml_check(

        db=db,

        transaction=transaction,

        transaction_data=ml_data
    )

    prediction = result["prediction"]

    # --------------------------------------------------------
    # If suspicious
    # --------------------------------------------------------

    if prediction["prediction"] == "SUSPICIOUS":

        notify_suspicious_transaction(

            db=db,

            customer_id=sender.customer_id,

            transaction_id=transaction.id
        )

        return {
            "transaction": transaction,

            "prediction": prediction,

            "status": "UNDER_REVIEW"
        }

    # --------------------------------------------------------
    # Normal transaction
    # --------------------------------------------------------

    sender.balance = (
        float(sender.balance) - amount
    )

    receiver.balance = (
        float(receiver.balance) + amount
    )

    transaction.status = "COMPLETED"

    db.commit()

    db.refresh(transaction)

    # --------------------------------------------------------
    # Customer notification
    # --------------------------------------------------------

    notify_transaction_completed(

        db=db,

        customer_id=sender.customer_id,

        transaction_id=transaction.id
    )

    return {

        "transaction": transaction,

        "prediction": prediction,

        "status": "COMPLETED"
    }