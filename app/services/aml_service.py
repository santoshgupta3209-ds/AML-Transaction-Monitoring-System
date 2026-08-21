from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.aml_alert import AMLAlert

from app.ml.predict import predict_transaction


def analyze_transaction(
    transaction_data: dict
):
    """
    Send transaction data to the trained
    AML machine learning model.
    """

    prediction = predict_transaction(
        transaction_data
    )

    return prediction


def create_aml_alert(
    db: Session,
    transaction: Transaction,
    prediction: dict
):
    """
    Create an AML alert when a transaction
    is detected as suspicious.
    """

    if prediction["prediction"] != "SUSPICIOUS":
        return None

    alert = AMLAlert(

        transaction_id=transaction.id,

        risk_score=prediction[
            "probability"
        ],

        risk_level=prediction[
            "risk_level"
        ],

        alert_type="SUSPICIOUS_TRANSACTION",

        description=(
            "Machine learning model detected "
            "potentially suspicious transaction."
        ),

        status="OPEN"
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def process_aml_check(
    db: Session,
    transaction: Transaction,
    transaction_data: dict
):
    """
    Complete AML analysis.
    """

    prediction = analyze_transaction(
        transaction_data
    )

    # Store ML result
    transaction.risk_probability = (
        prediction["probability"]
    )

    transaction.risk_level = (
        prediction["risk_level"]
    )

    if prediction["prediction"] == "SUSPICIOUS":

        transaction.status = "UNDER_REVIEW"

    else:

        transaction.status = "COMPLETED"

    db.commit()
    db.refresh(transaction)

    # Create alert if suspicious
    alert = create_aml_alert(
        db,
        transaction,
        prediction
    )

    return {
        "prediction": prediction,
        "transaction": transaction,
        "alert": alert
    }