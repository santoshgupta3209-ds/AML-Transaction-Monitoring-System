"""
AML Real-Time Prediction Module

Loads aml_model.pkl and predicts:
- NORMAL
- SUSPICIOUS

Also returns:
- suspicious probability
- risk level
"""

from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# Model path
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "app"
    / "ml"
    / "aml_model.pkl"
)


# ============================================================
# Risk Thresholds
# ============================================================

LOW_THRESHOLD = 0.40

HIGH_THRESHOLD = 0.70

HIGH_VALUE_TRANSACTION_THRESHOLD = 500000


# ============================================================
# Load Model
# ============================================================

def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "AML model not found.\n"
            "Please run train_model.py first.\n"
            f"Expected path: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# ============================================================
# Calculate Risk Level
# ============================================================

def get_risk_level(
    probability: float,
    amount: float = 0
) -> str:

    if amount >= HIGH_VALUE_TRANSACTION_THRESHOLD:
        return "HIGH"

    if probability < LOW_THRESHOLD:

        return "LOW"

    elif probability < HIGH_THRESHOLD:

        return "MEDIUM"

    else:

        return "HIGH"


# ============================================================
# Predict Transaction
# ============================================================

def predict_transaction(
    transaction_data: dict
):

    model = load_model()

    # Convert dictionary to DataFrame
    data = pd.DataFrame(
        [transaction_data]
    )

    # Prediction
    prediction = int(
        model.predict(data)[0]
    )

    # Suspicious probability
    probability = float(
        model.predict_proba(data)[0][1]
    )

    # Risk level
    amount = float(transaction_data.get("amount", 0))
    risk_level = get_risk_level(probability, amount)

    # Label
    if prediction == 1 or amount >= HIGH_VALUE_TRANSACTION_THRESHOLD:

        prediction_label = "SUSPICIOUS"

    else:

        prediction_label = "NORMAL"

    return {

        "prediction": prediction_label,

        "probability": round(
            probability,
            4
        ),

        "risk_level": risk_level
    }


# ============================================================
# Test Prediction
# ============================================================

if __name__ == "__main__":

    sample_transaction = {

        "amount": 85000,

        "transaction_type": "Transfer",

        "transaction_channel": "Online",

        "transaction_location": "Mumbai",

        "transaction_hour": 22,

        "transaction_frequency": 8,

        "average_transaction_amount": 12000,

        "account_age_days": 250,

        "previous_transaction_count": 100,

        "previous_suspicious_count": 3,

        "receiver_count": 12,

        "international_transaction": 0,

        "cash_transaction": 0,

        "balance_before": 150000,

        "balance_after": 65000
    }

    result = predict_transaction(
        sample_transaction
    )

    print("=" * 50)
    print("AML TRANSACTION PREDICTION")
    print("=" * 50)

    print(
        f"Prediction   : {result['prediction']}"
    )

    print(
        f"Probability  : {result['probability']}"
    )

    print(
        f"Risk Level   : {result['risk_level']}"
    )

    print("=" * 50)