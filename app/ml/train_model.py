"""
AML Machine Learning Training Script

Models:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. XGBoost

The best model is selected using F1 Score.
ROC-AUC is also reported because AML is a
classification problem with an important
suspicious-transaction class.
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from xgboost import XGBClassifier

from app.ml.preprocessing import create_preprocessor


# ============================================================
# Project Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "dataset" / "aml_transactions.csv"

MODEL_DIR = BASE_DIR / "app" / "ml"

BEST_MODEL_PATH = MODEL_DIR / "aml_model.pkl"

PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"

METRICS_PATH = MODEL_DIR / "model_metrics.json"


# ============================================================
# Target column
# ============================================================

TARGET_COLUMN = "label"


# ============================================================
# Main Training Function
# ============================================================

def train_model():

    print("=" * 70)
    print("AI-BASED ANTI-MONEY LAUNDERING MODEL TRAINING")
    print("=" * 70)

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------

    if not DATASET_PATH.exists():

        print("\nERROR: Dataset not found.")

        print(f"Expected location:")
        print(DATASET_PATH)

        sys.exit(1)

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    print("\n[1/8] Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {df.shape}")

    # --------------------------------------------------------
    # Basic cleaning
    # --------------------------------------------------------

    print("\n[2/8] Cleaning dataset...")

    # Remove duplicate rows
    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    print(f"Removed duplicates: {before - after}")

    # Check target
    if TARGET_COLUMN not in df.columns:

        raise ValueError(
            f"Target column '{TARGET_COLUMN}' "
            f"was not found in dataset."
        )

    # Remove rows where target is missing
    df = df.dropna(subset=[TARGET_COLUMN])

    # Make target integer
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)

    # --------------------------------------------------------
    # Import feature definitions
    # --------------------------------------------------------

    from app.ml.preprocessing import (
        NUMERICAL_FEATURES,
        CATEGORICAL_FEATURES
    )

    feature_columns = (
        NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
    )

    # Check features
    missing_features = [
        column
        for column in feature_columns
        if column not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing required features: "
            + ", ".join(missing_features)
        )

    # --------------------------------------------------------
    # X and y
    # --------------------------------------------------------

    print("\n[3/8] Preparing features...")

    X = df[feature_columns]

    y = df[TARGET_COLUMN]

    print(f"Features: {len(feature_columns)}")
    print(f"Samples: {len(X)}")

    print("\nClass distribution:")

    print(
        y.value_counts()
        .rename(
            index={
                0: "Normal",
                1: "Suspicious"
            }
        )
    )

    # --------------------------------------------------------
    # Train/Test Split
    # --------------------------------------------------------

    print("\n[4/8] Splitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples : {len(X_test)}")

    # --------------------------------------------------------
    # Models
    # --------------------------------------------------------

    print("\n[5/8] Creating models...")

    models = {

        "Logistic Regression":
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            ),

        "Decision Tree":
            DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=10,
                class_weight="balanced",
                random_state=42
            ),

        "Random Forest":
            RandomForestClassifier(
                n_estimators=250,
                max_depth=15,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            ),

        "XGBoost":
            XGBClassifier(
                n_estimators=250,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1
            )
    }

    # --------------------------------------------------------
    # Train models
    # --------------------------------------------------------

    print("\n[6/8] Training models...")

    results = {}

    best_model = None
    best_model_name = None
    best_f1 = -1

    for model_name, model in models.items():

        print("\n" + "-" * 70)
        print(f"Training: {model_name}")
        print("-" * 70)

        # Create a complete pipeline
        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    create_preprocessor()
                ),
                (
                    "model",
                    model
                )
            ]
        )

        # Train
        pipeline.fit(
            X_train,
            y_train
        )

        # Predictions
        y_pred = pipeline.predict(X_test)

        # Probability
        y_probability = pipeline.predict_proba(X_test)[:, 1]

        # Metrics
        accuracy = accuracy_score(
            y_test,
            y_pred
        )

        precision = precision_score(
            y_test,
            y_pred,
            zero_division=0
        )

        recall = recall_score(
            y_test,
            y_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            y_pred,
            zero_division=0
        )

        roc_auc = roc_auc_score(
            y_test,
            y_probability
        )

        cm = confusion_matrix(
            y_test,
            y_pred
        )

        results[model_name] = {

            "accuracy": round(float(accuracy), 6),

            "precision": round(float(precision), 6),

            "recall": round(float(recall), 6),

            "f1_score": round(float(f1), 6),

            "roc_auc": round(float(roc_auc), 6),

            "confusion_matrix": cm.tolist()
        }

        print(
            f"Accuracy  : {accuracy:.4f}"
        )

        print(
            f"Precision : {precision:.4f}"
        )

        print(
            f"Recall    : {recall:.4f}"
        )

        print(
            f"F1 Score  : {f1:.4f}"
        )

        print(
            f"ROC-AUC   : {roc_auc:.4f}"
        )

        # Select best model using F1
        if f1 > best_f1:

            best_f1 = f1

            best_model = pipeline

            best_model_name = model_name

    # --------------------------------------------------------
    # Save best model
    # --------------------------------------------------------

    print("\n[7/8] Saving best model...")

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        best_model,
        BEST_MODEL_PATH
    )

    # --------------------------------------------------------
    # Save preprocessing pipeline
    # --------------------------------------------------------

    # The preprocessor is already inside the complete pipeline.
    # Saving it separately is useful for inspection/reuse.

    preprocessor = best_model.named_steps[
        "preprocessor"
    ]

    joblib.dump(
        preprocessor,
        PREPROCESSOR_PATH
    )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    metrics_output = {

        "best_model": best_model_name,

        "selection_metric": "F1 Score",

        "dataset": str(DATASET_PATH),

        "training_samples": int(len(X_train)),

        "testing_samples": int(len(X_test)),

        "features": feature_columns,

        "models": results
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics_output,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print("\n[8/8] Training completed.")

    print("\n" + "=" * 70)
    print("AML MODEL TRAINING COMPLETED")
    print("=" * 70)

    print(f"\nBest Model: {best_model_name}")

    print(
        f"Best F1 Score: {best_f1:.4f}"
    )

    print("\nGenerated files:")

    print(
        f"✓ {BEST_MODEL_PATH.name}"
    )

    print(
        f"✓ {PREPROCESSOR_PATH.name}"
    )

    print(
        f"✓ {METRICS_PATH.name}"
    )

    print("\nBest Model Classification Report:")

    # Recalculate best predictions
    best_predictions = best_model.predict(X_test)

    print(
        classification_report(
            y_test,
            best_predictions,
            target_names=[
                "Normal",
                "Suspicious"
            ],
            zero_division=0
        )
    )

    print("=" * 70)


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    train_model()