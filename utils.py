"""
utils.py — small shared helpers so every script loads / splits data identically.

The cleaning done here is *explained and demonstrated step by step* in
02_Pandas_DataCleaning.py; this file is just the reusable final version.
"""
import matplotlib
matplotlib.use("Agg")                      # headless: save charts to files, no window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import (ALL_FEATURES, CATEGORICAL_FEATURES, FRAUD_CSV, INDIA_CSV,
                    NUMERIC_FEATURES, RANDOM_STATE, TARGET, TEST_SIZE, UPI2024_CSV)


# ----------------------------------------------------------------- loaders
def load_fraud() -> pd.DataFrame:
    """fraud_dataset.csv with structural NaNs made explicit."""
    df = pd.read_csv(FRAUD_CSV)
    # url_referrer / request_description are empty unless the session came from a link
    # or was a collection request -> "not applicable", not "unknown".
    for col in ("url_referrer", "request_description"):
        df[col] = df[col].fillna("none")
    return df


def load_upi2024() -> pd.DataFrame:
    """upi_transactions_2024.csv with snake_case columns and a real datetime."""
    df = pd.read_csv(UPI2024_CSV)
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_india() -> pd.DataFrame:
    """upi_fraud_india_dataset.csv (every row is a reported fraud)."""
    df = pd.read_csv(INDIA_CSV)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ------------------------------------------------------- preprocessing / split
def build_preprocessor() -> ColumnTransformer:
    """Impute -> scale numerics, impute -> one-hot categoricals (fit on TRAIN only)."""
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer(
        [("num", numeric, NUMERIC_FEATURES), ("cat", categorical, CATEGORICAL_FEATURES)],
        sparse_threshold=0.0,
    )


def make_split(df: pd.DataFrame | None = None):
    """Stratified 80/20 split — identical in every script (same random_state)."""
    if df is None:
        df = load_fraud()
    X, y = df[ALL_FEATURES], df[TARGET]
    return train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE)


# ------------------------------------------------------------------- plotting
def setup_plot_style():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 130, "axes.titleweight": "bold"})


def save_fig(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"   saved -> {path.name}")
