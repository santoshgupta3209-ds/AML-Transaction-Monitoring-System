from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):

    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    phone = Column(
        String(20),
        nullable=True
    )

    address = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(30),
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships

    user = relationship(
        "User",
        back_populates="customer"
    )

    accounts = relationship(
        "Account",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="customer",
        cascade="all, delete-orphan"
    )