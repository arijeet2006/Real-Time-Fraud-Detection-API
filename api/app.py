from pathlib import Path
import logging

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from src.redis_client import record_transaction
from src.kafka_producer import send_transaction


# Logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# FastAPI

app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="API for detecting fraudulent transactions",
    version="1.0.0",
)


# Model

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "fraud_detection_model.joblib"
)

model = joblib.load(MODEL_PATH)

FRAUD_THRESHOLD = 0.5


# Transaction schema

class Transaction(BaseModel):
    cc_num: str
    amt: float
    category: str
    gender: str
    state: str
    merchant: str
    lat: float
    long: float
    city_pop: int
    merch_lat: float
    merch_long: float
    is_night: int
    hour_sin: float
    hour_cos: float
    day_sin: float
    day_cos: float
    age: float
    distance_km: float
    customer_prior_tx_count: int
    amount_vs_customer_median: float
    tx_count_1h: int
    tx_count_24h: int


# Health check

@app.get("/")
def home():
    return {
        "message": "API is working"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
    }

# Prediction

@app.post("/predict")
def predict(transaction: Transaction):

    transaction_data = transaction.model_dump()

    send_transaction(transaction_data)

    customer_id = transaction_data.pop("cc_num")

    tx_count_1h = record_transaction(
        customer_id
    )

    transaction_data["tx_count_1h"] = tx_count_1h

    transaction_df = pd.DataFrame(
        [transaction_data]
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

    logger.info(
        "Prediction | customer=%s | tx_count_1h=%d | "
        "probability=%.6f | decision=%s",
        customer_id,
        tx_count_1h,
        probability,
        decision,
    )

    return {
        "fraud_probability": probability,
        "decision": decision,
        "tx_count_1h": tx_count_1h,
    }

@app.get("/redis-test")
def redis_test():

    count = record_transaction(
        "test_customer"
    )

    return {
        "customer": "test_customer",
        "tx_count_1h": count,
    }