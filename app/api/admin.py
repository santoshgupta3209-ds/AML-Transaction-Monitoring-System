from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.aml_alert import AMLAlert
from app.schemas.customer import AdminCustomerCreate, AdminCustomerUpdate
from app.schemas.account import AccountCreate, AccountUpdate
from app.security import hash_password
from app.services.notification_service import notify_account_frozen

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db)
):

    total_users = (
        db.query(User).count()
    )

    total_customers = (
        db.query(Customer).count()
    )

    total_accounts = (
        db.query(Account).count()
    )

    total_transactions = (
        db.query(Transaction).count()
    )

    total_alerts = (
        db.query(AMLAlert).count()
    )

    suspicious_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.status
            == "UNDER_REVIEW"
        )
        .count()
    )

    frozen_accounts = (
        db.query(Account)
        .filter(
            Account.status == "FROZEN"
        )
        .count()
    )

    return {

        "total_users":
            total_users,

        "total_customers":
            total_customers,

        "total_accounts":
            total_accounts,

        "total_transactions":
            total_transactions,

        "total_aml_alerts":
            total_alerts,

        "suspicious_transactions":
            suspicious_transactions,

        "frozen_accounts":
            frozen_accounts
    }


# ============================================================
# GET ALL CUSTOMERS
# ============================================================

@router.get("/customers")
def get_customers(
    db: Session = Depends(get_db)
):

    customers = (
        db.query(Customer)
        .all()
    )

    return [
        {
            "id": customer.id,
            "user_id": customer.user_id,
            "username": customer.user.username if customer.user else None,
            "email": customer.user.email if customer.user else None,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address,
            "status": customer.status,
            "created_at": customer.created_at,
            "accounts": [
                {
                    "id": account.id,
                    "account_number": account.account_number,
                    "account_type": account.account_type,
                    "balance": str(account.balance),
                    "status": account.status
                }
                for account in customer.accounts
            ]
        }
        for customer in customers
    ]


# ============================================================
# CREATE CUSTOMER WITH ACCOUNT
# ============================================================

@router.post("/customers")
def create_customer(
    customer_data: AdminCustomerCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(
            (User.username == customer_data.username)
            | (User.email == customer_data.email)
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    existing_account = (
        db.query(Account)
        .filter(Account.account_number == customer_data.account_number)
        .first()
    )

    if existing_account:

        raise HTTPException(
            status_code=400,
            detail="Account number already exists"
        )

    try:
        new_user = User(
            username=customer_data.username,
            email=customer_data.email,
            password_hash=hash_password(customer_data.password),
            role="CUSTOMER"
        )
        new_customer = Customer(
            user=new_user,
            full_name=customer_data.full_name,
            phone=customer_data.phone,
            address=customer_data.address,
            status=customer_data.status
        )
        new_account = Account(
            customer=new_customer,
            account_number=customer_data.account_number,
            account_type=customer_data.account_type,
            balance=customer_data.balance,
            status="ACTIVE"
        )

        db.add(new_user)
        db.flush()
        db.commit()
        db.refresh(new_user)
        db.refresh(new_customer)
        db.refresh(new_account)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username, email, or account number already exists"
        )

    return {
        "customer": {
            "id": new_customer.id,
            "user_id": new_customer.user_id,
            "full_name": new_customer.full_name,
            "phone": new_customer.phone,
            "address": new_customer.address,
            "status": new_customer.status
        },
        "account": {
            "id": new_account.id,
            "account_number": new_account.account_number,
            "account_type": new_account.account_type,
            "balance": str(new_account.balance),
            "status": new_account.status
        }
    }


# ============================================================
# GET CUSTOMER BY ID
# ============================================================

@router.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "customer": {
            "id": customer.id,
            "user_id": customer.user_id,
            "username": customer.user.username,
            "email": customer.user.email,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address,
            "status": customer.status,
            "accounts": [
                {
                    "id": account.id,
                    "account_number": account.account_number,
                    "account_type": account.account_type,
                    "balance": str(account.balance),
                    "status": account.status
                }
                for account in customer.accounts
            ]
        }
    }


# ============================================================
# UPDATE CUSTOMER PROFILE
# ============================================================

@router.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    customer_data: AdminCustomerUpdate,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    user = customer.user
    if not user:
        raise HTTPException(
            status_code=500,
            detail="Associated user record not found"
        )

    if customer_data.username is not None:
        existing_user = (
            db.query(User)
            .filter(User.username == customer_data.username, User.id != user.id)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already in use"
            )
        user.username = customer_data.username

    if customer_data.email is not None:
        existing_user = (
            db.query(User)
            .filter(User.email == customer_data.email, User.id != user.id)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already in use"
            )
        user.email = customer_data.email

    if customer_data.password is not None:
        user.password_hash = hash_password(customer_data.password)

    if customer_data.full_name is not None:
        customer.full_name = customer_data.full_name

    if customer_data.phone is not None:
        customer.phone = customer_data.phone

    if customer_data.address is not None:
        customer.address = customer_data.address

    if customer_data.status is not None:
        customer.status = customer_data.status

    account = customer.accounts[0] if customer.accounts else None
    if account_data := customer_data:
        if account and customer_data.account_number is not None:
            existing_account = (
                db.query(Account)
                .filter(Account.account_number == customer_data.account_number, Account.id != account.id)
                .first()
            )
            if existing_account:
                raise HTTPException(
                    status_code=400,
                    detail="Account number already exists"
                )
            account.account_number = customer_data.account_number

        if account and customer_data.account_type is not None:
            account.account_type = customer_data.account_type

        if account and customer_data.balance is not None:
            account.balance = customer_data.balance

    db.commit()
    db.refresh(customer)

    return {
        "message": "Customer updated successfully",
        "customer": {
            "id": customer.id,
            "user_id": customer.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address,
            "status": customer.status
        }
    }


# ============================================================
# DELETE CUSTOMER
# ============================================================

@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    user = (
        db.query(User)
        .filter(User.id == customer.user_id)
        .first()
    )

    db.delete(customer)

    if user:
        db.delete(user)

    db.commit()

    return {
        "message": "Customer and user deleted successfully",
        "customer_id": customer_id
    }


# ============================================================
# CREATE ACCOUNT FOR CUSTOMER
# ============================================================

@router.post("/customers/{customer_id}/accounts")
def create_account(
    customer_id: int,
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    existing_account = (
        db.query(Account)
        .filter(Account.account_number == account_data.account_number)
        .first()
    )

    if existing_account:

        raise HTTPException(
            status_code=400,
            detail="Account number already exists"
        )

    account = Account(
        customer_id=customer.id,
        account_number=account_data.account_number,
        account_type=account_data.account_type,
        balance=account_data.balance,
        status="ACTIVE"
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {
        "message": "Account created successfully",
        "account": {
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "status": account.status
        }
    }


# ============================================================
# UPDATE ACCOUNT
# ============================================================

@router.put("/accounts/{account_id}")
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):

    account = (
        db.query(Account)
        .filter(Account.id == account_id)
        .first()
    )

    if not account:

        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if account_data.account_type is not None:
        account.account_type = account_data.account_type

    if account_data.status is not None:
        account.status = account_data.status

    db.commit()
    db.refresh(account)

    return {
        "message": "Account updated successfully",
        "account": {
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "status": account.status
        }
    }


# ============================================================
# DELETE ACCOUNT
# ============================================================

@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):

    account = (
        db.query(Account)
        .filter(Account.id == account_id)
        .first()
    )

    if not account:

        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    linked_transactions = (
        db.query(Transaction)
        .filter(
            (Transaction.sender_account_id == account.id)
            | (Transaction.receiver_account_id == account.id)
        )
        .count()
    )

    if linked_transactions:
        account.status = "DELETED"
        db.commit()
        return {
            "message": "Account deleted while transaction history was preserved",
            "account_id": account_id,
            "status": account.status
        }

    db.delete(account)
    db.commit()

    return {
        "message": "Account deleted successfully",
        "account_id": account_id
    }


# ============================================================
# GET ALL TRANSACTIONS
# ============================================================

@router.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .order_by(
            Transaction.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": transaction.id,
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "transaction_channel": transaction.transaction_channel,
            "transaction_location": transaction.transaction_location,
            "risk_probability": transaction.risk_probability,
            "risk_level": transaction.risk_level,
            "status": transaction.status,
            "created_at": transaction.created_at,
            "debit": {
                "customer_name": transaction.sender_account.customer.full_name,
                "account_number": transaction.sender_account.account_number,
            },
            "credit": {
                "customer_name": transaction.receiver_account.customer.full_name,
                "account_number": transaction.receiver_account.account_number,
            },
        }
        for transaction in transactions
    ]


# ============================================================
# GET AML ALERTS
# ============================================================

@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db)
):

    alerts = (
        db.query(AMLAlert)
        .order_by(
            AMLAlert.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": alert.id,
            "transaction_id": alert.transaction_id,
            "amount": alert.transaction.amount,
            "transaction_type": alert.transaction.transaction_type,
            "transaction_channel": alert.transaction.transaction_channel,
            "transaction_location": alert.transaction.transaction_location,
            "transaction_created_at": alert.transaction.created_at,
            "risk_score": alert.risk_score,
            "risk_level": alert.risk_level,
            "alert_type": alert.alert_type,
            "description": alert.description,
            "status": alert.status,
            "created_at": alert.created_at,
            "customer": {
                "id": alert.transaction.sender_account.customer.id,
                "name": alert.transaction.sender_account.customer.full_name,
                "phone": alert.transaction.sender_account.customer.phone,
                "account_number": alert.transaction.sender_account.account_number,
                "account_status": alert.transaction.sender_account.status,
            },
            "debit": {
                "customer_id": alert.transaction.sender_account.customer.id,
                "customer_name": alert.transaction.sender_account.customer.full_name,
                "account_number": alert.transaction.sender_account.account_number,
            },
            "credit": {
                "customer_id": alert.transaction.receiver_account.customer.id,
                "customer_name": alert.transaction.receiver_account.customer.full_name,
                "account_number": alert.transaction.receiver_account.account_number,
            },
        }
        for alert in alerts
    ]


@router.put("/alerts/{alert_id}/close")
def close_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(AMLAlert)
        .filter(AMLAlert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.status = "CLOSED"
    alert.resolved_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Alert closed successfully",
        "alert_id": alert.id,
        "status": alert.status
    }


# ============================================================
# FREEZE ACCOUNT
# ============================================================

@router.put("/accounts/{account_id}/freeze")
def freeze_account(
    account_id: int,
    db: Session = Depends(get_db)
):

    account = (
        db.query(Account)
        .filter(
            Account.id == account_id
        )
        .first()
    )

    if not account:

        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    account.status = "FROZEN"

    db.commit()

    notify_account_frozen(db, account.customer_id)

    return {
        "message":
            "Account frozen successfully",

        "account_id":
            account.id,

        "status":
            account.status
    }


# ============================================================
# UNFREEZE ACCOUNT
# ============================================================

@router.put("/accounts/{account_id}/unfreeze")
def unfreeze_account(
    account_id: int,
    db: Session = Depends(get_db)
):

    account = (
        db.query(Account)
        .filter(
            Account.id == account_id
        )
        .first()
    )

    if not account:

        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    account.status = "ACTIVE"

    db.commit()

    return {
        "message":
            "Account unfrozen successfully",

        "account_id":
            account.id,

        "status":
            account.status
    }