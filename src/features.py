import numpy as np
import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create fraud-detection features using the same logic
    validated in the feature engineering notebook.
    """

    df = df.copy()

    # 1. Drop identifiers / free-text columns

    df = df.drop(
        columns=[
            "street",
            "city",
            "first",
            "last",
            "job",
            "trans_num",
            "unix_time",
            "zip",
        ],
        errors="ignore",
    )

    # 2. Transaction timestamp

    df["trans_date_trans_time"] = pd.to_datetime(
        df["trans_date_trans_time"],
        errors="coerce",
    )

    transaction_time = df["trans_date_trans_time"]

    # 3. Time features

    df["hour"] = transaction_time.dt.hour

    day_of_week = transaction_time.dt.dayofweek

    df["is_night"] = (
        (df["hour"] >= 22) | (df["hour"] <= 3)
    ).astype(int)

    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )

    df["day_sin"] = np.sin(
        2 * np.pi * day_of_week / 7
    )

    df["day_cos"] = np.cos(
        2 * np.pi * day_of_week / 7
    )

    # 4. Customer age

    dob = pd.to_datetime(
        df["dob"],
        errors="coerce",
    )

    df["age"] = (
        transaction_time - dob
    ).dt.days / 365.25

    # 5. Distance between customer and merchant
    #    Haversine distance in kilometers

    lat1 = np.radians(df["lat"])
    lat2 = np.radians(df["merch_lat"])

    dlat = lat2 - lat1

    dlon = np.radians(
        df["merch_long"] - df["long"]
    )

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    df["distance_km"] = (
        6371
        * 2
        * np.arcsin(np.sqrt(a.clip(0, 1)))
    )

    # 6. Customer historical features
    #    Uses ONLY transactions before current transaction

    df = df.sort_values(
        ["cc_num", "trans_date_trans_time"]
    ).reset_index(drop=True)

    prior_median = (
        df.groupby("cc_num")["amt"]
        .transform(
            lambda amounts:
            amounts.shift()
            .expanding(min_periods=1)
            .median()
        )
    )

    df["customer_prior_tx_count"] = (
        df.groupby("cc_num")
        .cumcount()
    )

    df["amount_vs_customer_median"] = (
        np.log1p(df["amt"])
        - np.log1p(prior_median)
    ).fillna(0)

    # 7. Transaction velocity
    #    Excludes the current transaction

    rolling_source = (
        df.assign(_transaction=1)
        .set_index("trans_date_trans_time")
    )

    for window, feature in [
        ("1h", "tx_count_1h"),
        ("24h", "tx_count_24h"),
    ]:
        counts = (
            rolling_source
            .groupby("cc_num")["_transaction"]
            .rolling(
                window,
                closed="left",
            )
            .sum()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        df[feature] = (
            counts
            .fillna(0)
            .to_numpy(dtype="int32")
        )

    return df