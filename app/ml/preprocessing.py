"""
AML Model Preprocessing

This module defines:
- Input features
- Numerical features
- Categorical features
- ColumnTransformer preprocessing pipeline
"""

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer


# ============================================================
# Features used by the AML model
# ============================================================

NUMERICAL_FEATURES = [
    "amount",
    "transaction_hour",
    "transaction_frequency",
    "average_transaction_amount",
    "account_age_days",
    "previous_transaction_count",
    "previous_suspicious_count",
    "receiver_count",
    "international_transaction",
    "cash_transaction",
    "balance_before",
    "balance_after",
]


CATEGORICAL_FEATURES = [
    "transaction_type",
    "transaction_channel",
    "transaction_location",
]


# ============================================================
# Create preprocessing pipeline
# ============================================================

def create_preprocessor():

    # Numerical preprocessing
    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            ),
            (
                "scaler",
                StandardScaler()
            )
        ]
    )

    # Categorical preprocessing
    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )

    # Combine numerical + categorical preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                NUMERICAL_FEATURES
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            )
        ]
    )

    return preprocessor