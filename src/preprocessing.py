# src/preprocessing.py

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sklearn.model_selection import StratifiedKFold


# Feature columns

cat_cols = [
    "category",
    "gender",
    "state",
]

merchant_col = [
    "merchant",
]

num_cols = [
    "amt",
    "lat",
    "long",
    "city_pop",
    "merch_lat",
    "merch_long",
    "is_night",
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "age",
    "distance_km",
    "customer_prior_tx_count",
    "amount_vs_customer_median",
    "tx_count_1h",
    "tx_count_24h",
]


# All model features

feature_cols = (
    cat_cols
    + merchant_col
    + num_cols
)

# Preprocessor

preprocessor = ColumnTransformer(
    [
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            cat_cols,
        ),
        (
            "merchant_target",
            TargetEncoder(
                target_type="binary",
                smooth="auto",
                cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            ),
            merchant_col,
        ),
        (
            "numeric",
            StandardScaler(),
            num_cols,
        ),
    ]
)