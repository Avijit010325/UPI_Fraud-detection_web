"""
02 — Pandas: inspection, cleaning, GroupBy, pivot, MERGE  (Modules 3 & 4)

All three CSVs are used here:
  * fraud_dataset.csv           - missing values, duplicates, outliers, groupby / pivot
  * upi_transactions_2024.csv   - cleaning column names + datetime, groupby
  * upi_fraud_india_dataset.csv - state-level fraud reports
  * MERGE: 2024 transaction volume (per state)  +  reported fraud cases (per state)

Note for pandas 3.0 users: we never use chained `df[col].fillna(x, inplace=True)`;
we always assign back:  df[col] = df[col].fillna(x)
"""
import numpy as np
import pandas as pd

from config import ALL_FEATURES, OUT, TARGET
from utils import load_india, load_upi2024

pd.set_option("display.width", 200, "display.max_columns", 30)
raw = pd.read_csv("data/fraud_dataset.csv")          # RAW copy so we can show the cleaning steps

# =========================================================== A. inspection
print("=" * 78, "\nA. FIRST LOOK")
print("fraud_dataset :", raw.shape, "| memory", f"{raw.memory_usage(deep=True).sum() / 1e6:.1f} MB")
print("dtype counts  :", raw.dtypes.astype(str).value_counts().to_dict())
print(f"class balance : {raw[TARGET].value_counts().to_dict()} -> fraud = {raw[TARGET].mean():.1%}")

# ===================================================== B. missing values
print("=" * 78, "\nB. MISSING VALUES")
miss = raw.isna().sum()
miss = miss[miss > 0].to_frame("missing")
miss["pct"] = (miss["missing"] / len(raw) * 100).round(1)
print(miss)
print("-> ~97% missing is not random. url_referrer only exists when the session came from a link;")
print("   request_description only exists for collection requests. So NaN means 'not applicable'.")
df = raw.copy()
for col in ("url_referrer", "request_description"):
    df[col] = df[col].fillna("none")                 # assign back (pandas-3 safe)
print("after fillna('none'): missing =", int(df.isna().sum().sum()))

const = [c for c in df.columns if df[c].nunique() <= 1]
print("constant columns (no information, drop candidates):", const)

# ============================================================ C. duplicates
print("=" * 78, "\nC. DUPLICATES")
print("duplicate rows            :", int(df.duplicated().sum()))
print("duplicate transaction_ids :", int(df["transaction_id"].duplicated().sum()))
before = len(df)
df = df.drop_duplicates(subset="transaction_id")
print(f"drop_duplicates(subset='transaction_id'): {before} -> {len(df)} rows")

# ===================================================== D. types & renaming
print("=" * 78, "\nD. DATA TYPES / COLUMN NAMES")
print("fraud_dataset timestamp examples:", raw["timestamp"].head(3).tolist(),
      "-> only 'mm:ss.f' survives: hour/date are lost, so this column is UNUSABLE.")
print("   we use transaction_time_of_day (0-23) as the hour instead.")
up = pd.read_csv("data/upi_transactions_2024.csv")
print("upi_2024 raw columns :", list(up.columns[:5]), "...  (spaces and brackets are awkward)")
up = load_upi2024()                                  # snake_case + parsed datetime
print("upi_2024 clean cols  :", list(up.columns[:5]), "...")
print("timestamp dtype now  :", up["timestamp"].dtype, "| range", up["timestamp"].min().date(), "->", up["timestamp"].max().date())
up["month"] = up["timestamp"].dt.month
print("hour_of_day matches timestamp:", bool((up["timestamp"].dt.hour == up["hour_of_day"]).all()))

# ========================================================= E. outliers (IQR)
print("=" * 78, "\nE. OUTLIERS — IQR RULE ON amount")
q1, q3 = df["amount"].quantile([0.25, 0.75])
iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
is_out = (df["amount"] < lo) | (df["amount"] > hi)
print(f"Q1={q1:,.0f} Q3={q3:,.0f} IQR={iqr:,.0f} -> fences [{lo:,.0f}, {hi:,.0f}]")
print(f"outliers: {int(is_out.sum())} ({is_out.mean():.1%})")
print(f"fraud rate inside outliers = {df.loc[is_out, TARGET].mean():.1%}  vs  outside = {df.loc[~is_out, TARGET].mean():.1%}")
print("DECISION: we KEEP them. Here the 'outliers' are the fraud. Deleting them would delete the signal.")
print("          For plotting we use log scale; for linear models StandardScaler / RobustScaler handles scale.")
df["amount_capped"] = df["amount"].clip(lower=lo, upper=hi)   # winsorised version, for comparison only
print(f"skewness raw={df['amount'].skew():.2f}  capped={df['amount_capped'].skew():.2f}  log1p={np.log1p(df['amount']).skew():.2f}")

u_q1, u_q3 = up["amount_inr"].quantile([0.25, 0.75])
u_hi = u_q3 + 1.5 * (u_q3 - u_q1)
print(f"upi_2024 amount_inr: upper fence {u_hi:,.0f}, outliers {(up['amount_inr'] > u_hi).mean():.1%}")

# ========================================================= F. GroupBy & pivot
print("=" * 78, "\nF. GROUPBY / AGG / PIVOT")
df["hour_bucket"] = pd.cut(df["transaction_time_of_day"], bins=[-1, 5, 11, 17, 23],
                           labels=["Night 0-5", "Morning 6-11", "Afternoon 12-17", "Evening 18-23"])
by_hour = df.groupby("hour_bucket", observed=True)[TARGET].agg(transactions="count", fraud_rate="mean").round(3)
print("\nfraud rate by time of day:\n", by_hour)

by_auth = df.groupby("authentication_attempts")[TARGET].agg(transactions="count", fraud_rate="mean").round(3)
print("\nfraud rate by authentication attempts:\n", by_auth)

summary = df.groupby(TARGET).agg(avg_amount=("amount", "mean"), median_amount=("amount", "median"),
                                 avg_session=("session_duration", "mean"),
                                 avg_pin_speed=("pin_entry_speed", "mean")).round(2)
print("\nclass profile (named aggregation):\n", summary)

pivot = df.pivot_table(index="hour_bucket", columns="session_source", values=TARGET,
                       aggfunc="mean", observed=True).round(3)
print("\npivot: fraud rate by time-of-day x session source:\n", pivot)

print("\nupi_2024 — failed-transaction rate by network type:")
print(up.assign(failed=(up["transaction_status"] == "FAILED"))
        .groupby("network_type")["failed"].agg(transactions="count", failed_rate="mean").round(4))
print("upi_2024 — fraud_flag rate by device (tiny base rate 0.19%, differences are noise):")
print(up.groupby("device_type")["fraud_flag"].agg(transactions="count", flagged="sum", rate="mean").round(4))

# ============================================================== G. MERGE
print("=" * 78, "\nG. MERGE — state-level exposure (2024 volume  +  reported fraud cases)")
india = load_india()
volume = (up.groupby("sender_state")
            .agg(total_txns=("transaction_id", "size"), total_value_inr=("amount_inr", "sum"),
                 avg_txn_inr=("amount_inr", "mean"))
            .reset_index())
reports = (india.groupby("victim_state")
                .agg(reported_cases=("transaction_id", "size"), total_lost_inr=("amount_inr", "sum"),
                     avg_loss_inr=("amount_inr", "mean"))
                .reset_index())
print(f"volume table: {len(volume)} states | reports table: {len(reports)} states")

# keys have DIFFERENT column names in the two tables -> left_on / right_on
outer = volume.merge(reports, left_on="sender_state", right_on="victim_state", how="outer", indicator=True)
print("\nouter merge with indicator -> who matched?\n", outer["_merge"].value_counts().to_string())
print("states only in the fraud reports (no 2024 volume, cannot compute a rate):",
      sorted(outer.loc[outer["_merge"] == "right_only", "victim_state"]))

inner = volume.merge(reports, left_on="sender_state", right_on="victim_state", how="inner").drop(columns="victim_state")
inner = inner.rename(columns={"sender_state": "state"})
inner["cases_per_100k_txns"] = (inner["reported_cases"] / inner["total_txns"] * 100_000).round(1)
inner = inner.sort_values("cases_per_100k_txns", ascending=False)
print("\nINNER merge (10 states present in both):")
print(inner[["state", "total_txns", "reported_cases", "total_lost_inr", "cases_per_100k_txns"]].to_string(index=False))
print("\nCAVEAT: the two files are separate simulations and the reports file has only 1,000 rows,")
print("        so this is an ILLUSTRATIVE state view, not a true per-state fraud rate.")
inner.to_csv(OUT / "state_level_summary.csv", index=False)
print("saved -> outputs/state_level_summary.csv")

# ================================================== H. save modelling table
print("=" * 78, "\nH. SAVE CLEAN MODELLING TABLE")
clean = df[ALL_FEATURES + [TARGET]]
clean.to_csv(OUT / "fraud_clean_modelling_table.csv", index=False)
print(f"saved -> outputs/fraud_clean_modelling_table.csv  {clean.shape}")
