from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship

from app.database import Base


class AMLAlert(Base):

    __tablename__ = "aml_alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False,
        unique=True
    )

    risk_score = Column(
        Float,
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False
    )

    alert_type = Column(
        String(100),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        default="OPEN"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    # Relationship

    transaction = relationship(
        "Transaction",
        back_populates="aml_alert"
    )