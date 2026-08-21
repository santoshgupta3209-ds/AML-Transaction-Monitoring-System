from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate

from app.ml.predict import predict_transaction
from app.services.aml_service import create_aml_alert
from app.security import get_current_customer
from app.models.user import User

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# ============================================================
# CREATE TRANSACTION
# ============================================================

@router.post("/send")
def send_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_customer)
):

    sender_account_number = transaction_data.sender_account.strip()
    receiver_account_number = transaction_data.receiver_account.strip()

    # --------------------------------------------------------
    # Find sender
    # --------------------------------------------------------

    sender = (
        db.query(Account)
        .filter(
            Account.account_number
            == sender_account_number
        )
        .first()
    )

    if not sender:

        raise HTTPException(
            status_code=404,
            detail=f"Sender account '{sender_account_number}' not found"
        )

    if sender.customer.user_id != current_customer.id:
        raise HTTPException(
            status_code=403,
            detail="You can only send transactions from your own account"
        )

    # --------------------------------------------------------
    # Find receiver
    # --------------------------------------------------------

    receiver = (
        db.query(Account)
        .filter(
            Account.account_number
            == receiver_account_number
        )
        .first()
    )

    if not receiver:

        raise HTTPException(
            status_code=404,
            detail=f"Receiver account '{receiver_account_number}' not found"
        )

    # --------------------------------------------------------
    # Check sender status
    # --------------------------------------------------------

    if sender.status != "ACTIVE":

        raise HTTPException(
            status_code=403,
            detail="Your account is frozen. Please contact your bank."
        )

    # --------------------------------------------------------
    # Check balance
    # --------------------------------------------------------

    if sender.balance < transaction_data.amount:

        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    # --------------------------------------------------------
    # Prepare ML transaction data
    # --------------------------------------------------------

    ml_data = {

        "amount":
            transaction_data.amount,

        "transaction_type":
            transaction_data.transaction_type,

        "transaction_channel":
            transaction_data.transaction_channel,

        "transaction_location":
            transaction_data.transaction_location,

        "transaction_hour":
            transaction_data.transaction_hour,

        "transaction_frequency":
            transaction_data.transaction_frequency,

        "average_transaction_amount":
            transaction_data.average_transaction_amount,

        "account_age_days":
            transaction_data.account_age_days,

        "previous_transaction_count":
            transaction_data.previous_transaction_count,

        "previous_suspicious_count":
            transaction_data.previous_suspicious_count,

        "receiver_count":
            transaction_data.receiver_count,

        "international_transaction":
            transaction_data.international_transaction,

        "cash_transaction":
            transaction_data.cash_transaction,

        "balance_before":
            sender.balance,

        "balance_after":
            sender.balance - transaction_data.amount
    }

    # --------------------------------------------------------
    # ML Prediction
    # --------------------------------------------------------

    prediction = predict_transaction(
        ml_data
    )

    # --------------------------------------------------------
    # Determine transaction status
    # --------------------------------------------------------

    if prediction["prediction"] == "SUSPICIOUS":

        transaction_status = "UNDER_REVIEW"

    else:

        transaction_status = "COMPLETED"

    # --------------------------------------------------------
    # Create transaction
    # --------------------------------------------------------

    new_transaction = Transaction(

        sender_account_id=sender.id,

        receiver_account_id=receiver.id,

        amount=transaction_data.amount,

        transaction_type=
            transaction_data.transaction_type,

        transaction_channel=
            transaction_data.transaction_channel,

        transaction_location=
            transaction_data.transaction_location,

        risk_probability=
            prediction["probability"],

        risk_level=
            prediction["risk_level"],

        status=transaction_status
    )

    db.add(new_transaction)

    # --------------------------------------------------------
    # Complete normal transaction
    # --------------------------------------------------------

    if transaction_status == "COMPLETED":

        sender.balance -= transaction_data.amount

        receiver.balance += transaction_data.amount

    db.commit()

    db.refresh(new_transaction)

    create_aml_alert(
        db,
        new_transaction,
        prediction
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "message":
            "Transaction processed",

        "transaction_id":
            new_transaction.id,

        "status":
            transaction_status,

        "prediction":
            prediction["prediction"],

        "risk_probability":
            prediction["probability"],

        "risk_level":
            prediction["risk_level"]
    }


# ============================================================
# GET TRANSACTION
# ============================================================

@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id
        )
        .first()
    )

    if not transaction:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction