from datetime import date, datetime, time, timedelta
from calendar import monthrange

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.security import get_current_customer

router = APIRouter(
    prefix="/customer",
    tags=["Customer"]
)

@router.get("/transaction-summary")
def customer_transaction_summary(
    period: str = "month",
    selected_date: str | None = None,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_customer)
):
    """Return debit and credit totals for the signed-in customer."""

    account_ids = [
        account.id
        for account in db.query(Account).join(Customer).filter(
            Customer.user_id == current_customer.id
        ).all()
    ]

    if not account_ids:
        return {"period": period, "transaction_count": 0, "debit_amount": 0, "credit_amount": 0}

    try:
        anchor = date.fromisoformat(selected_date) if selected_date else date.today()
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Use a valid date in YYYY-MM-DD format") from error

    normalized_period = period.strip().lower()
    if normalized_period == "date":
        start_date, end_date = anchor, anchor + timedelta(days=1)
    elif normalized_period == "week":
        start_date = anchor - timedelta(days=anchor.weekday())
        end_date = start_date + timedelta(days=7)
    elif normalized_period == "month":
        start_date = anchor.replace(day=1)
        end_date = start_date.replace(day=monthrange(start_date.year, start_date.month)[1]) + timedelta(days=1)
    elif normalized_period == "year":
        start_date = anchor.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    else:
        raise HTTPException(status_code=400, detail="Period must be Date, Week, Month, or Year")

    transactions = db.query(Transaction).filter(
        ((Transaction.sender_account_id.in_(account_ids))
         | (Transaction.receiver_account_id.in_(account_ids))),
        Transaction.created_at >= datetime.combine(start_date, time.min),
        Transaction.created_at < datetime.combine(end_date, time.min)
    ).all()

    debit = sum(
        (transaction.amount for transaction in transactions
         if transaction.sender_account_id in account_ids),
        0
    )
    credit = sum(
        (transaction.amount for transaction in transactions
         if transaction.receiver_account_id in account_ids),
        0
    )

    return {
        "period": normalized_period,
        "transaction_count": len(transactions),
        "debit_amount": debit,
        "credit_amount": credit
    }


@router.get("/transactions")
def customer_transactions(
    from_date: str | None = None,
    to_date: str | None = None,
    account_number: str | None = None,
    transaction_type: str | None = None,
    direction: str | None = None,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_customer)
):
    """Return only transactions belonging to the signed-in customer."""

    customer_account_ids = {
        account.id
        for account in db.query(Account).join(Customer).filter(
            Customer.user_id == current_customer.id
        ).all()
    }

    query = (
        db.query(Transaction)
        .join(
            Account,
            (Transaction.sender_account_id == Account.id)
            | (Transaction.receiver_account_id == Account.id)
        )
        .join(Customer, Account.customer_id == Customer.id)
        .filter(Customer.user_id == current_customer.id)
        .distinct()
    )

    try:
        if from_date:
            query = query.filter(Transaction.created_at >= datetime.combine(
                date.fromisoformat(from_date), time.min
            ))
        if to_date:
            query = query.filter(Transaction.created_at < datetime.combine(
                date.fromisoformat(to_date) + timedelta(days=1), time.min
            ))
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail="Use valid dates in YYYY-MM-DD format"
        ) from error

    if account_number:
        account = (
            db.query(Account)
            .join(Customer)
            .filter(
                Customer.user_id == current_customer.id,
                Account.account_number == account_number
            )
            .first()
        )
        if not account:
            raise HTTPException(status_code=400, detail="Account filter is not valid")
        query = query.filter(
            (Transaction.sender_account_id == account.id)
            | (Transaction.receiver_account_id == account.id)
        )

    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)

    if direction:
        normalized_direction = direction.strip().upper()
        if normalized_direction == "DEBIT":
            query = query.filter(Transaction.sender_account_id.in_(customer_account_ids))
        elif normalized_direction == "CREDIT":
            query = query.filter(Transaction.receiver_account_id.in_(customer_account_ids))
        else:
            raise HTTPException(
                status_code=400,
                detail="Direction must be Debit or Credit"
            )

    transactions = query.order_by(Transaction.created_at.desc()).all()

    return [
        {
            "id": transaction.id,
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "risk_level": transaction.risk_level,
            "status": transaction.status,
            "created_at": transaction.created_at,
            "direction": (
                "Send"
                if transaction.sender_account_id in customer_account_ids
                else "Received"
            ),
            "customer_name": (
                transaction.receiver_account.customer.full_name
                if transaction.sender_account_id in customer_account_ids
                else transaction.sender_account.customer.full_name
            ),
            "account": (
                transaction.sender_account.account_number
                if transaction.sender_account_id in customer_account_ids
                else transaction.receiver_account.account_number
            )
        }
        for transaction in transactions
    ]


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

@router.get("/dashboard/{user_id}")
def customer_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    accounts = (
        db.query(Account)
        .filter(Account.customer_id == customer.id)
        .all()
    )

    return {
        "customer": {
            "id": customer.id,
            "name": customer.full_name,
            "email": user.email
        },
        "accounts": [
            {
                "account_id": account.id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": account.balance,
                "status": account.status
            }
            for account in accounts
        ]
    }


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@router.get("/profile/{user_id}")
def customer_profile(
    user_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "customer_id": customer.id,
        "user_id": customer.user_id,
        "name": customer.full_name,
        "phone": customer.phone,
        "address": customer.address,
        "status": customer.status
    }