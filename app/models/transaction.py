from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Float
)

from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sender_account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False
    )

    receiver_account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False
    )

    amount = Column(
        Numeric(15, 2),
        nullable=False
    )

    transaction_type = Column(
        String(50),
        nullable=False
    )

    transaction_channel = Column(
        String(50),
        nullable=False
    )

    transaction_location = Column(
        String(100),
        nullable=True
    )

    # ML result

    risk_probability = Column(
        Float,
        nullable=True
    )

    risk_level = Column(
        String(20),
        nullable=True
    )

    status = Column(
        String(30),
        default="COMPLETED"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships

    sender_account = relationship(
        "Account",
        foreign_keys=[sender_account_id],
        back_populates="sent_transactions"
    )

    receiver_account = relationship(
        "Account",
        foreign_keys=[receiver_account_id],
        back_populates="received_transactions"
    )

    aml_alert = relationship(
        "AMLAlert",
        back_populates="transaction",
        uselist=False
    )