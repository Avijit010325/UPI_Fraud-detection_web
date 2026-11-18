"""
03 — Data visualisation (Module 5): 13 chart types across the three CSVs.

  upi_transactions_2024.csv   -> charts 1-4, 10, 13   (volume, categories, states, devices, hour x weekday)
  fraud_dataset.csv           -> charts 5-7, 9, 11    (how fraud differs from legitimate)
  upi_fraud_india_dataset.csv -> charts 8, 12         (fraud types, victims, recovery)

Charts are saved to outputs/charts/.  Run:  python 03_Visualization.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import CHARTS, NUMERIC_FEATURES, TARGET
from utils import load_fraud, load_india, load_upi2024, save_fig, setup_plot_style

setup_plot_style()
up, fr, ind = load_upi2024(), load_fraud(), load_india()
LEGIT, FRAUD = "#2a9d8f", "#e63946"
CLASS_PALETTE = {0: LEGIT, 1: FRAUD}
fr["class"] = fr[TARGET].map({0: "Legitimate", 1: "Fraud"})
CLASS_NAMED = {"Legitimate": LEGIT, "Fraud": FRAUD}
print("Creating charts...")

# 1. LINE — monthly volume (2024) -------------------------------------------------
monthly = up.groupby(up["timestamp"].dt.to_period("M")).size()
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly.index.strftime("%b"), monthly.values, marker="o", color="#264653", linewidth=2)
ax.set(title="1. Line — UPI transactions per month (2024)", xlabel="Month", ylabel="Transactions")
ax.set_ylim(0, monthly.max() * 1.15)
save_fig(fig, CHARTS / "01_line_monthly_volume.png")

# 2. BAR — merchant categories ----------------------------------------------------
cat = up["merchant_category"].value_counts()
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=cat.index, y=cat.values, hue=cat.index, palette="viridis", legend=False, ax=ax)
ax.set(title="2. Bar — transactions by merchant category", xlabel="", ylabel="Transactions")
ax.tick_params(axis="x", rotation=30)
save_fig(fig, CHARTS / "02_bar_merchant_category.png")

# 3. HORIZONTAL BAR — states ------------------------------------------------------
st = up["sender_state"].value_counts().sort_values()
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.barh(st.index, st.values, color="#457b9d")
ax.set(title="3. Horizontal bar — transactions by sender state", xlabel="Transactions")
save_fig(fig, CHARTS / "03_barh_states.png")

# 4. HISTOGRAM — amount distribution (log10) -------------------------------------
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(np.log10(up["amount_inr"].clip(lower=1)), bins=50, color="#e9c46a", edgecolor="white")
ax.set(title="4. Histogram — UPI amount, log10 scale (right-skewed data)", xlabel="log10(amount in INR)", ylabel="Count")
save_fig(fig, CHARTS / "04_histogram_amount_log.png")

# 5. BOX PLOT — amount by class ----------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4.5))
sns.boxplot(data=fr, x="class", y="amount", hue="class", palette=CLASS_NAMED, legend=False, ax=ax)
ax.set_yscale("log")
ax.set(title="5. Box plot — amount by class (log axis)", xlabel="", ylabel="Amount (log scale)")
save_fig(fig, CHARTS / "05_box_amount_by_class.png")

# 6. VIOLIN — session duration by class -------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4.5))
sns.violinplot(data=fr, x="class", y="session_duration", hue="class", palette=CLASS_NAMED,
               inner="quartile", legend=False, ax=ax)
ax.set(title="6. Violin — session duration by class", xlabel="", ylabel="Seconds")
save_fig(fig, CHARTS / "06_violin_session_duration.png")

# 7. SCATTER — amount vs amount-relative-to-history -------------------------------
samp = fr.sample(3000, random_state=42)
fig, ax = plt.subplots(figsize=(7, 5))
sns.scatterplot(data=samp, x="amount", y="transaction_amount_vs_sender_history", hue="class",
                palette=CLASS_NAMED, alpha=0.55, s=18, ax=ax)
ax.set(xscale="log", yscale="log", title="7. Scatter — amount vs. amount relative to sender history",
       xlabel="Amount (log)", ylabel="Amount / usual amount (log)")
save_fig(fig, CHARTS / "07_scatter_amount_vs_history.png")

# 8. PIE — fraud types (India reports) --------------------------------------------
ft = ind["fraud_type"].value_counts()
top = pd.concat([ft.head(6), pd.Series({"Other": ft.iloc[6:].sum()})])
fig, ax = plt.subplots(figsize=(6.5, 6))
ax.pie(top.values, labels=top.index, autopct="%1.0f%%", startangle=90,
       colors=sns.color_palette("Set2", len(top)), wedgeprops={"edgecolor": "white"})
ax.set_title("8. Pie — reported UPI fraud by type (India reports)")
save_fig(fig, CHARTS / "08_pie_fraud_types.png")

# 9. HEATMAP — correlation matrix -------------------------------------------------
corr = fr[NUMERIC_FEATURES + [TARGET]].corr()
fig, ax = plt.subplots(figsize=(9, 7.5))
sns.heatmap(corr, cmap="coolwarm", center=0, annot=True, fmt=".2f", annot_kws={"size": 6.5},
            cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title("9. Heatmap — feature correlation (incl. is_fraud)")
save_fig(fig, CHARTS / "09_heatmap_correlation.png")

# 10. COUNT PLOT — device x network ------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5))
sns.countplot(data=up, x="device_type", hue="network_type", palette="mako", ax=ax)
ax.set(title="10. Count plot — device type split by network", xlabel="", ylabel="Transactions")
save_fig(fig, CHARTS / "10_countplot_device_network.png")

# 11. KDE — hour of day by class ---------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.kdeplot(data=fr, x="transaction_time_of_day", hue="class", palette=CLASS_NAMED,
            fill=True, alpha=0.35, common_norm=False, bw_adjust=0.8, clip=(0, 23), ax=ax)
ax.set(title="11. KDE — time of day: fraud clusters at night", xlabel="Hour of day (0-23)", ylabel="Density")
save_fig(fig, CHARTS / "11_kde_hour_by_class.png")

# 12. STACKED BAR — victim age group x recovery status ---------------------------
ct = pd.crosstab(ind["victim_age_group"], ind["recovery_status"])
ct = ct.reindex(sorted(ct.index))
ax = ct.plot(kind="bar", stacked=True, figsize=(8, 4.5), colormap="Set2", edgecolor="white")
ax.set(title="12. Stacked bar — victims by age group and recovery outcome", xlabel="Victim age group", ylabel="Reported cases")
ax.tick_params(axis="x", rotation=0)
save_fig(ax.get_figure(), CHARTS / "12_stacked_bar_age_recovery.png")

# 13. HEATMAP — hour x weekday volume ---------------------------------------------
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
grid = (up.pivot_table(index="day_of_week", columns="hour_of_day", values="transaction_id", aggfunc="count")
          .reindex(order))
fig, ax = plt.subplots(figsize=(11, 4))
sns.heatmap(grid, cmap="YlGnBu", cbar_kws={"label": "Transactions"}, ax=ax)
ax.set(title="13. Heatmap — when do people use UPI? (weekday x hour)", xlabel="Hour of day", ylabel="")
save_fig(fig, CHARTS / "13_heatmap_hour_weekday.png")

print(f"\nDone — {len(list(CHARTS.glob('[0-1][0-9]_*.png')))} charts in outputs/charts/")
