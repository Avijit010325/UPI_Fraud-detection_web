"""
06 — Supervised learning (Modules 7, 8, 9): Logistic Regression, Decision Tree,
Random Forest, SVM — with the metrics that matter for FRAUD.

Flow
  1. Dummy baseline  (shows why accuracy alone is misleading with 17% fraud)
  2. Cross-validation on the TRAIN set only  -> used to compare / choose models
  3. Final evaluation on the untouched TEST set
  4. Threshold trade-off (precision vs recall) for the chosen model
  5. Interpretability: LR odds ratios, decision-tree rules, RF importances
  6. Save the deployed pipeline + metadata for the Flask app
"""
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix, f1_score,
                             precision_recall_curve, precision_score, recall_score, roc_auc_score,
                             roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, export_text

from config import (ALL_FEATURES, CATEGORICAL_FEATURES, CHARTS, MODELS, NUMERIC_FEATURES, OUT,
                    RANDOM_STATE, TARGET)
from utils import build_preprocessor, load_fraud, make_split, save_fig, setup_plot_style

setup_plot_style()
pd.set_option("display.width", 200, "display.max_columns", 30)
df = load_fraud()
X_train, X_test, y_train, y_test = make_split(df)
print(f"train={len(X_train)} test={len(X_test)} | fraud share train={y_train.mean():.3f} test={y_test.mean():.3f}")

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
    "Decision Tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, class_weight="balanced",
                                            random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                                            n_jobs=-1, random_state=RANDOM_STATE),
    "SVM (RBF)": SVC(kernel="rbf", C=1.0, class_weight="balanced"),
}
pipes = {name: Pipeline([("prep", build_preprocessor()), ("model", m)]) for name, m in models.items()}

# ------------------------------------------------------------------ 1. baseline
print("\n1. BASELINE — always predict 'legitimate'")
dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
d_pred = dummy.predict(X_test)
print(f"   accuracy={accuracy_score(y_test, d_pred):.1%}  recall={recall_score(y_test, d_pred):.1%}")
print("   => 'accuracy' of ~83% for a model that catches ZERO fraud. Accuracy is the wrong yardstick here.")

# ------------------------------------------------------- 2. cross-validation
print("\n2. 5-FOLD STRATIFIED CROSS-VALIDATION (train set only)")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_rows = []
for name, pipe in pipes.items():
    f1 = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)
    cv_rows.append((name, f1.mean(), f1.std()))
    print(f"   {name:20s} F1 = {f1.mean():.3f} ± {f1.std():.3f}")
cv_table = pd.DataFrame(cv_rows, columns=["model", "cv_f1_mean", "cv_f1_std"]).set_index("model")

# --------------------------------------------------------- 3. final evaluation
print("\n3. FINAL EVALUATION ON THE HELD-OUT TEST SET")
results, scores, preds = [], {}, {}
for name, pipe in pipes.items():
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    score = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else pipe.decision_function(X_test)
    scores[name], preds[name] = score, pred
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    results.append({
        "model": name,
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred),
        "recall": recall_score(y_test, pred),
        "f1": f1_score(y_test, pred),
        "roc_auc": roc_auc_score(y_test, score),
        "pr_auc": average_precision_score(y_test, score),
        "missed_fraud_FN": fn,
        "false_alarms_FP": fp,
    })
res = pd.DataFrame(results).set_index("model")
res = res.join(cv_table)
print(res.round(3).to_string())
res.round(4).to_csv(OUT / "model_comparison.csv")
print("\n   FN = fraud we MISSED (money lost);  FP = legit payments we blocked (annoyed customers).")

# ---- charts: ROC, confusion matrices
fig, ax = plt.subplots(figsize=(6.5, 5.5))
for name in models:
    fpr, tpr, _ = roc_curve(y_test, scores[name])
    ax.plot(fpr, tpr, label=f"{name} (AUC={res.loc[name, 'roc_auc']:.3f})", linewidth=2)
ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random guess")
ax.set(title="ROC curves — test set", xlabel="False positive rate", ylabel="True positive rate")
ax.legend(loc="lower right")
save_fig(fig, CHARTS / "06a_roc_curves.png")

fig, axes = plt.subplots(1, 4, figsize=(16, 3.8))
for ax, name in zip(axes, models):
    sns.heatmap(confusion_matrix(y_test, preds[name]), annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                xticklabels=["Legit", "Fraud"], yticklabels=["Legit", "Fraud"])
    ax.set(title=name, xlabel="Predicted", ylabel="Actual")
save_fig(fig, CHARTS / "06b_confusion_matrices.png")

# ------------------------------------------ choose the deployed model
deployable = [n for n in models if hasattr(pipes[n], "predict_proba")]      # SVC has no probabilities by default
best = res.loc[deployable, "cv_f1_mean"].idxmax()                          # chosen by CV, NOT by test score
print(f"\nDeployed model = {best}  (highest cross-validated F1 among models that output probabilities)")

# ----------------------------------------------------- 4. threshold trade-off
print(f"\n4. THRESHOLD TRADE-OFF for {best} (default cut-off is 0.5, but it is a business decision)")
p = scores[best]
rows = []
for t in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
    pr = (p >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pr).ravel()
    rows.append((t, precision_score(y_test, pr), recall_score(y_test, pr), f1_score(y_test, pr), fn, fp))
thr = pd.DataFrame(rows, columns=["threshold", "precision", "recall", "f1", "missed_fraud", "false_alarms"])
print(thr.round(3).to_string(index=False))
print("   Lower threshold -> catch more fraud, but block more honest users. Banks usually accept extra")
print("   false alarms (an OTP or a call) rather than missed fraud (lost money) -> recall is prioritised.")

prec, rec, _ = precision_recall_curve(y_test, p)
fig, ax = plt.subplots(figsize=(6.5, 5))
ax.plot(rec, prec, color="#e63946", linewidth=2)
ax.axhline(y_test.mean(), ls="--", color="grey", label=f"Random baseline ({y_test.mean():.2f})")
ax.set(title=f"Precision-Recall curve — {best}", xlabel="Recall", ylabel="Precision", ylim=(0, 1.02))
ax.legend()
save_fig(fig, CHARTS / "06c_precision_recall.png")

# ------------------------------------------------------ 5. interpretability
print("\n5. INTERPRETABILITY")
names = [n.split("__")[1] for n in pipes["Random Forest"].named_steps["prep"].get_feature_names_out()]

lr = pipes["Logistic Regression"].named_steps["model"]
odds = pd.Series(np.exp(lr.coef_[0]), index=names).sort_values(ascending=False)
print("Logistic Regression odds ratios per +1 standard deviation (scaled features), top 5 / bottom 3:")
print(odds.head(5).round(2).to_string(), "\n...")
print(odds.tail(3).round(2).to_string())
print("   >1 raises fraud odds, <1 lowers them.  Correlated features (auth attempts, failed txns, velocity, OTP")
print("   requests correlate 0.8-0.9) share credit, so individual coefficients are less stable — a known LR caveat.")

dt = pipes["Decision Tree"].named_steps["model"]
print("\nDecision Tree — top 3 levels as if/else rules (features are scaled, so thresholds are z-scores):")
print(export_text(dt, feature_names=names, max_depth=3))

rf = pipes["Random Forest"].named_steps["model"]
imp = pd.Series(rf.feature_importances_, index=names).sort_values()
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(imp.index, imp.values, color="#2a9d8f")
ax.set(title="Random Forest feature importance", xlabel="Importance (mean decrease in impurity)")
save_fig(fig, CHARTS / "06d_rf_feature_importance.png")
print("Top 5 RF features:", imp.sort_values(ascending=False).head(5).round(3).to_dict())

# ------------------------------------------------------ 6. save for Flask
print("\n6. SAVING DEPLOYED MODEL")
final = pipes[best]
legit = df[df[TARGET] == 0]
meta = {
    "model_name": best,
    "threshold": 0.5,
    "numeric_features": NUMERIC_FEATURES,
    "categorical_features": CATEGORICAL_FEATURES,
    "categories": {c: sorted(df[c].unique().tolist()) for c in CATEGORICAL_FEATURES},
    "legit_median": {c: float(legit[c].median()) for c in NUMERIC_FEATURES},
    "min": {c: float(df[c].min()) for c in NUMERIC_FEATURES},
    "max": {c: float(df[c].max()) for c in NUMERIC_FEATURES},
    "test_metrics": {k: round(float(res.loc[best, k]), 4) for k in ("accuracy", "precision", "recall", "f1", "roc_auc")},
}
joblib.dump(final, MODELS / "fraud_model.joblib")
(MODELS / "model_meta.json").write_text(json.dumps(meta, indent=2))
print(f"   saved models/fraud_model.joblib and models/model_meta.json  ({best})")
print("   test metrics:", meta["test_metrics"])
