"""
05 — K-Means clustering (Module 10): can we find suspicious behaviour WITHOUT labels?

Important honesty point for the viva:
  * The label (is_fraud) is NOT given to K-Means.  Features are scaled numeric behaviour only.
  * We look at the label AFTER clustering, purely to grade the result (external validation).
    That does not make it supervised: the clusters were formed without seeing it.

Steps: scale -> elbow -> silhouette -> fit -> PCA picture -> cluster profiles
       -> post-hoc fraud rate per cluster -> distance-to-centroid anomaly score.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from config import CHARTS, NUMERIC_FEATURES, OUT, RANDOM_STATE, TARGET
from utils import load_fraud, save_fig, setup_plot_style

setup_plot_style()
pd.set_option("display.width", 220, "display.max_columns", 30)
df = load_fraud()
X = StandardScaler().fit_transform(df[NUMERIC_FEATURES])     # K-Means is distance-based -> scaling is mandatory
y = df[TARGET].to_numpy()
base_rate = y.mean()
print(f"{X.shape[0]} transactions, {X.shape[1]} scaled numeric features (label NOT used). Base fraud rate {base_rate:.1%}")

# ------------------------------------------------ 1. elbow + silhouette
print("\n1. CHOOSING K")
ks = range(1, 11)
inertia = [KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X).inertia_ for k in ks]
sil = {}
for k in range(2, 9):
    lab = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit_predict(X)
    sil[k] = silhouette_score(X, lab, sample_size=5000, random_state=RANDOM_STATE)   # sample: O(n^2) otherwise
print("inertia :", {k: round(v) for k, v in zip(ks, inertia)})
print("silhouette:", {k: round(v, 3) for k, v in sil.items()})
best_k = max(sil, key=sil.get)
print(f"highest silhouette at k={best_k} ({sil[best_k]:.3f}).  Silhouette: 1 = tight & separated, 0 = overlapping, <0 = wrong cluster.")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(list(ks), inertia, marker="o", color="#264653")
axes[0].axvline(best_k, ls="--", color="#e63946", label=f"chosen k={best_k}")
axes[0].set(title="Elbow method", xlabel="k", ylabel="Inertia (within-cluster SS)")
axes[0].legend()
axes[1].plot(list(sil), list(sil.values()), marker="o", color="#2a9d8f")
axes[1].set(title="Silhouette score", xlabel="k", ylabel="Silhouette")
save_fig(fig, CHARTS / "05a_elbow_silhouette.png")

# ------------------------------------------------ 2. final model
K = best_k
km = KMeans(n_clusters=K, n_init=10, random_state=RANDOM_STATE).fit(X)
df["cluster"] = km.labels_
print(f"\n2. FINAL K-MEANS  k={K}  sizes: {df['cluster'].value_counts().sort_index().to_dict()}")

# ------------------------------------------------ 3. PCA picture
pca = PCA(n_components=2, random_state=RANDOM_STATE)
P = pca.fit_transform(X)
print(f"PCA 2 components explain {pca.explained_variance_ratio_.sum():.0%} of variance (picture is a squashed view of 14-D space)")
idx = np.random.default_rng(RANDOM_STATE).choice(len(P), size=min(6000, len(P)), replace=False)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.scatterplot(x=P[idx, 0], y=P[idx, 1], hue=df["cluster"].to_numpy()[idx], palette="Set2", s=10, alpha=0.6, ax=axes[0])
axes[0].set(title=f"K-Means clusters (k={K}) in PCA space", xlabel="PC1", ylabel="PC2")
sns.scatterplot(x=P[idx, 0], y=P[idx, 1], hue=np.where(y[idx] == 1, "Fraud", "Legitimate"),
                palette={"Fraud": "#e63946", "Legitimate": "#2a9d8f"}, s=10, alpha=0.6, ax=axes[1])
axes[1].set(title="Same points coloured by the TRUE label (checked afterwards)", xlabel="PC1", ylabel="PC2")
save_fig(fig, CHARTS / "05b_kmeans_pca.png")

# ------------------------------------------------ 4. profiles + post-hoc validation
print("\n3. CLUSTER PROFILES (means of the original, unscaled features)")
prof_cols = ["amount", "transaction_amount_vs_sender_history", "authentication_attempts",
             "failed_transaction_count", "pin_entry_speed", "time_pressure_indicators", "unusual_device_flag"]
prof = df.groupby("cluster")[prof_cols].mean().round(2)
prof.insert(0, "size", df["cluster"].value_counts().sort_index())
prof["fraud_rate"] = df.groupby("cluster")[TARGET].mean().round(3)     # <- label used ONLY here, to grade
prof["share_of_all_fraud"] = (df.groupby("cluster")[TARGET].sum() / y.sum()).round(3)
print(prof.to_string())
prof.to_csv(OUT / "kmeans_cluster_profiles.csv")
top = prof["fraud_rate"].idxmax()
print(f"\nCluster {top} has fraud rate {prof.loc[top, 'fraud_rate']:.1%} vs {base_rate:.1%} overall  "
      f"-> unsupervised structure lines up with fraud (lift x{prof.loc[top, 'fraud_rate'] / base_rate:.1f}).")
print(f"BUT that cluster holds only {prof.loc[top, 'share_of_all_fraud']:.0%} of all fraud: K-Means isolated ONE tight, extreme")
print("pattern (many auth attempts, failed payments, very fast PIN entry). The other fraud looks 'normal'")
print("in cluster terms and stays hidden in the big cluster. High silhouette here is driven by that small,")
print("extreme group — so silhouette alone would not tell us the clusters cover all fraud.")

# ------------------------------------------------ 4b. is the "best" k the whole story?
print("\n3b. SENSITIVITY — how much fraud sits in near-pure fraud clusters (>99% fraud) for other k?")
sens = []
for k_alt in (2, 3, 4, 5):
    lab = KMeans(n_clusters=k_alt, n_init=10, random_state=RANDOM_STATE).fit_predict(X)
    t = pd.DataFrame({"c": lab, "y": y}).groupby("c")["y"].agg(size="size", rate="mean", frauds="sum")
    pure = t[t["rate"] > 0.99]
    sens.append((k_alt, len(pure), int(pure["size"].sum()), f"{pure['frauds'].sum() / y.sum():.0%}", f"{sil.get(k_alt, float('nan')):.3f}"))
print(pd.DataFrame(sens, columns=["k", "pure_fraud_clusters", "rows_in_them", "share_of_all_fraud", "silhouette"]).to_string(index=False))
print("Reading: silhouette prefers k=2, but k=3 splits a SECOND all-fraud group off (visible as the top blob")
print("in the PCA picture). Metrics guide the choice of k; they do not replace looking at the clusters.")

# ------------------------------------------------ 5. anomaly score
print("\n4. ANOMALY DETECTION — distance to the nearest centroid")
dist = km.transform(X).min(axis=1)
df["anomaly_score"] = dist
rows = []
for pct in (0.02, 0.05, 0.10):
    cut = np.quantile(dist, 1 - pct)
    flagged = dist >= cut
    prec = y[flagged].mean()
    rec = y[flagged].sum() / y.sum()
    rows.append((f"top {pct:.0%}", int(flagged.sum()), f"{prec:.1%}", f"{prec / base_rate:.1f}x", f"{rec:.1%}"))
print(pd.DataFrame(rows, columns=["flagged", "n", "fraud rate inside", "lift vs base", "share of all fraud caught"]).to_string(index=False))
print("Reading: the farther a transaction is from every cluster centre, the more likely it is fraud —")
print("found with zero labels. This is why unsupervised learning is useful when labels are scarce or late.")

fig, ax = plt.subplots(figsize=(8, 4))
sns.kdeplot(x=np.log1p(dist[y == 0]), fill=True, alpha=0.4, color="#2a9d8f", label="Legitimate", ax=ax)
sns.kdeplot(x=np.log1p(dist[y == 1]), fill=True, alpha=0.4, color="#e63946", label="Fraud", ax=ax)
ax.set(title="Distance to nearest centroid (log scale)", xlabel="log(1 + distance)", ylabel="Density")
ax.legend()
save_fig(fig, CHARTS / "05c_anomaly_distance.png")

print("\nCaveat: K-Means assumes roughly spherical, similar-size clusters and is sensitive to scaling and outliers.")
