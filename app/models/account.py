from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


class Account(Base):

    __tablename__ = "accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    account_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    account_type = Column(
        String(30),
        default="SAVINGS"
    )

    balance = Column(
        Numeric(15, 2),
        default=0
    )

    status = Column(
        String(30),
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Customer relationship

    customer = relationship(
        "Customer",
        back_populates="accounts"
    )

    # Transaction relationships

    sent_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_account_id",
        back_populates="sender_account"
    )

    received_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_account_id",
        back_populates="receiver_account"
    )