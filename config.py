"""
config.py — single source of truth for paths and the modelling feature list.

DATASET ROLES (see README):
  fraud_dataset.csv           -> MODELLING  (K-Means, LR/DT/RF/SVM, Flask app)
  upi_transactions_2024.csv   -> EDA / visualisation + state-level merge
  upi_fraud_india_dataset.csv -> fraud-type context + state-level merge (all rows are fraud)
  upi_data_new1.xlsx          -> evaluated and REJECTED (see 00_Dataset_Selection.py)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
MODELS = ROOT / "models"

FRAUD_CSV = DATA / "fraud_dataset.csv"
UPI2024_CSV = DATA / "upi_transactions_2024.csv"
INDIA_CSV = DATA / "upi_fraud_india_dataset.csv"
XLSX = DATA / "upi_data_new1.xlsx"          # optional; only used by script 00

for _p in (OUT, CHARTS, MODELS):
    _p.mkdir(parents=True, exist_ok=True)

TARGET = "is_fraud"
RANDOM_STATE = 42
TEST_SIZE = 0.20

# ---------------------------------------------------------------------------
# Modelling features for fraud_dataset.csv
#
# Policy (explained and measured in 04_Encoding_Preprocessing.py):
#   1. Drop any column that fails the leakage audit (a single feature that
#      almost reconstructs the label: receiver_account_age, handle_verification_status,
#      merchant_category_code == 'unknown', ...).
#   2. Keep compact behavioural signals that a payment app can observe at
#      transaction time. Skip the "scenario marker" columns (handle_*, request_*,
#      screen-mirroring columns) - each is filled by only one synthetic fraud recipe.
# ---------------------------------------------------------------------------
NUMERIC_FEATURES = [
    "amount",
    "transaction_amount_vs_sender_history",   # amount / sender's usual amount
    "transaction_time_of_day",               # hour 0-23
    "authentication_attempts",
    "failed_transaction_count",
    "transaction_velocity",
    "session_duration",
    "geographic_disparity",
    "pin_entry_speed",
    "otp_request_frequency",
    "time_pressure_indicators",
    "input_timing_consistency",
    "unusual_device_flag",
    "unusual_ip_flag",          # (unusual_location_flag is an exact duplicate of this -> dropped)
]
CATEGORICAL_FEATURES = ["session_source", "pin_entry_method"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Columns that only identify a row (never used as features)
ID_LIKE_COLUMNS = [
    "transaction_id", "user_id", "merchant_id", "timestamp",
    "description", "device_id", "ip_address", "location",
]
