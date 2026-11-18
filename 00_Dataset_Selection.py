"""
00 — WHY THIS DATASET?  (evidence for the "why did you pick fraud_dataset.csv" question)

We were given four UPI datasets. Before modelling we ran the same quick baseline
(Random Forest, 100 trees, class-weighted) on every labelled one and compared:

  * ROC-AUC  : 0.5 = coin flip, 1.0 = perfect
  * PR-AUC   : average precision; the honest metric when fraud is rare
               (a random model scores about the fraud rate itself)

A dataset is only useful for supervised learning if the features actually carry
signal about the label. Run:  python 00_Dataset_Selection.py
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

from config import ALL_FEATURES, OUT, RANDOM_STATE, TARGET, XLSX
from utils import load_fraud, load_india, load_upi2024


def baseline(X: pd.DataFrame, y: pd.Series):
    X = pd.get_dummies(X).astype(float)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
    rf = RandomForestClassifier(n_estimators=100, min_samples_leaf=5, class_weight="balanced",
                                n_jobs=-1, random_state=RANDOM_STATE).fit(Xtr, ytr)
    p = rf.predict_proba(Xte)[:, 1]
    return roc_auc_score(yte, p), average_precision_score(yte, p)


rows = []

# 1. fraud_dataset.csv  (clean behavioural feature set — see script 04 for the leakage audit)
df = load_fraud()
auc, ap = baseline(df[ALL_FEATURES], df[TARGET])
rows.append(("fraud_dataset.csv", len(df), df[TARGET].mean() * 100, auc, ap,
             "USE — real signal in behavioural features"))

# 2. upi_transactions_2024.csv
u = load_upi2024()
auc, ap = baseline(u.drop(columns=["transaction_id", "timestamp", "fraud_flag"]), u["fraud_flag"])
rows.append(("upi_transactions_2024.csv", len(u), u["fraud_flag"].mean() * 100, auc, ap,
             "EDA only — features carry ~no signal (AUC≈0.5)"))

# 3. upi_data_new1.xlsx  (optional: 500k rows, slow to read)
if XLSX.exists():
    x = pd.read_excel(XLSX)
    auc, ap = baseline(x.drop(columns=["fraud_risk"]), x["fraud_risk"])
    rows.append(("upi_data_new1.xlsx", len(x), x["fraud_risk"].mean() * 100, auc, ap,
                 "REJECT — anonymised codes, ~no signal (AUC≈0.5)"))
else:
    print("(data/upi_data_new1.xlsx not found — skipping it. Copy it into data/ to include it.)")

# 4. upi_fraud_india_dataset.csv
i = load_india()
rows.append(("upi_fraud_india_dataset.csv", len(i), i[TARGET].mean() * 100, float("nan"), float("nan"),
             "CONTEXT only — every row is fraud, no legitimate class to learn from"))

table = pd.DataFrame(rows, columns=["dataset", "rows", "fraud_%", "roc_auc", "pr_auc", "verdict"])
pd.set_option("display.width", 200, "display.max_colwidth", 70)
print("\n" + table.round(3).to_string(index=False))
table.round(4).to_csv(OUT / "dataset_comparison.csv", index=False)
print("\nsaved -> outputs/dataset_comparison.csv")
