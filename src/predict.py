from pathlib import Path

import joblib
import pandas as pd


# Model path

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "fraud_detection_model.joblib"
)

# Load complete pipeline

model = joblib.load(MODEL_PATH)


# Fraud threshold

FRAUD_THRESHOLD = 0.5

# Prediction function

def predict_fraud(transaction: dict) -> dict:
    """
    Predict fraud probability and decision
    for one already-feature-engineered transaction.
    """

    transaction_df = pd.DataFrame(
        [transaction]
    )

    probability = float(
        model.predict_proba(
            transaction_df
        )[0, 1]
    )

    decision = (
        "BLOCK"
        if probability >= FRAUD_THRESHOLD
        else "ALLOW"
    )

    return {
        "fraud_probability": probability,
        "decision": decision,
    }