from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.features import create_features
from src.preprocessing import feature_cols, preprocessor

# Paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "fraudTrain.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "Models"
    / "fraud_detection_model.joblib"
)


# Load raw data

df = pd.read_csv(DATA_PATH)

# Feature engineering

df = create_features(df)


# Chronological train / validation split

df = (
    df.sort_values("trans_date_trans_time")
    .reset_index(drop=True)
)

split_idx = int(len(df) * 0.8)

train_df = df.iloc[:split_idx]
valid_df = df.iloc[split_idx:]


# Features and target

X_train = train_df[feature_cols]
y_train = train_df["is_fraud"]

X_valid = valid_df[feature_cols]
y_valid = valid_df["is_fraud"]


# XGBoost

xgb_model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="auc",
    random_state=42,
    n_jobs=-1,
)


# Complete ML pipeline
# preprocessing → XGBoost

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", xgb_model),
    ]
)


# Train

model.fit(
    X_train,
    y_train,
)


# Validation

validation_probabilities = model.predict_proba(
    X_valid
)[:, 1]

print("Training completed.")
print(f"Training rows: {len(train_df)}")
print(f"Validation rows: {len(valid_df)}")
print(
    f"Validation fraud rate: "
    f"{y_valid.mean():.6f}"
)


# Save complete pipeline

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

joblib.dump(
    model,
    MODEL_PATH,
)

print(f"Model saved to: {MODEL_PATH}")