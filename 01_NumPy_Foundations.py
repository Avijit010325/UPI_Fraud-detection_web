"""
01 — NumPy foundations (Module 2), demonstrated on the real UPI fraud data.

Covers: arrays & attributes, indexing / boolean masks, aggregation with axis,
broadcasting, vectorisation vs loops, np.where / np.select, np.unique,
reshape / stack, seeded randomness, correlation & linear algebra.
"""
import time

import numpy as np

from config import NUMERIC_FEATURES, TARGET
from utils import load_fraud

df = load_fraud()

# ------------------------------------------------------------------ 1. arrays
print("=" * 70, "\n1. ARRAYS & ATTRIBUTES")
amount = df["amount"].to_numpy()                     # 1-D float array
X = df[NUMERIC_FEATURES].to_numpy(dtype=float)       # 2-D: rows = transactions, cols = features
y = df[TARGET].to_numpy()
print(f"amount : shape={amount.shape} dtype={amount.dtype} ndim={amount.ndim} size={amount.size}")
print(f"X      : shape={X.shape}  ({X.nbytes / 1e6:.1f} MB)")
print("creation helpers:", np.zeros(3), np.ones(3), np.arange(0, 10, 3), np.linspace(0, 1, 5), np.full(3, 7))
print("astype: first amounts as int ->", amount[:3].astype(int), "(truncates, does not round)")

# ------------------------------------------------------------- 2. indexing
print("=" * 70, "\n2. INDEXING, SLICING, BOOLEAN MASKS")
hour = df["transaction_time_of_day"].to_numpy()
print("first 5 amounts          :", amount[:5].round(1))
print("every 5000th amount      :", amount[::5000].round(1))
big = amount > 20_000
print(f"amount > 20,000          : {big.sum()} transactions ({big.mean():.1%})")
night_big = (hour < 5) & (amount > 20_000)          # note: & not 'and', parentheses required
print(f"night (<5am) AND > 20k   : {night_big.sum()} transactions, fraud rate {y[night_big].mean():.1%}")
print("fancy indexing rows 0,2,4 col 0:", X[[0, 2, 4], 0].round(1))

# ------------------------------------------------------------ 3. aggregation
print("=" * 70, "\n3. AGGREGATION (axis=0 -> per column)")
print(f"amount  mean={amount.mean():,.0f}  median={np.median(amount):,.0f}  std={amount.std():,.0f}")
print("mean > median  => right-skewed (a few very large payments pull the mean up)")
print("percentiles 50/90/99:", np.percentile(amount, [50, 90, 99]).round(0))
print(f"mean amount  fraud={amount[y == 1].mean():,.0f}  legit={amount[y == 0].mean():,.0f}")
col_means = X.mean(axis=0)
print("per-feature means (first 4):", {k: round(float(v), 2) for k, v in zip(NUMERIC_FEATURES[:4], col_means[:4])})

# ------------------------------------------------------------ 4. broadcasting
print("=" * 70, "\n4. BROADCASTING")
print(f"X {X.shape}  -  mean {col_means.shape}   -> shapes align from the right, {col_means.shape} is stretched to {X.shape}")
Z = (X - X.mean(axis=0)) / X.std(axis=0)             # z-score every column without a loop
print("z-scored column means ≈ 0 :", np.allclose(Z.mean(axis=0), 0, atol=1e-8))
print("z-scored column stds  ≈ 1 :", np.allclose(Z.std(axis=0), 1))
mn, mx = X.min(axis=0), X.max(axis=0)
X_minmax = (X - mn) / (mx - mn)                      # min-max scaling to [0, 1]
print(f"min-max range: [{X_minmax.min():.1f}, {X_minmax.max():.1f}]")

# ------------------------------------------- 5. vectorisation vs Python loop
print("=" * 70, "\n5. VECTORISATION (why NumPy exists)")
t0 = time.perf_counter()
total_loop = 0.0
for a in amount:
    total_loop += a * a
t_loop = time.perf_counter() - t0
t0 = time.perf_counter()
total_vec = np.dot(amount, amount)
t_vec = time.perf_counter() - t0
print(f"sum of squares  loop={t_loop * 1000:.2f} ms  vectorised={t_vec * 1000:.3f} ms  "
      f"-> ~{t_loop / max(t_vec, 1e-9):.0f}x faster, same answer: {np.isclose(total_loop, total_vec)}")

# ----------------------------------------------------- 6. where / select / unique
print("=" * 70, "\n6. np.where / np.select / np.unique")
ratio = df["transaction_amount_vs_sender_history"].to_numpy()
risk_flag = np.where(ratio > 3, "HIGH", "normal")
flag_counts = {str(k): int(v) for k, v in zip(*np.unique(risk_flag, return_counts=True))}
print("ratio>3 flag counts:", flag_counts)
band = np.select([amount < 1_000, amount < 10_000], ["small", "medium"], default="large")
band_counts = {str(k): int(v) for k, v in zip(*np.unique(band, return_counts=True))}
print("amount bands:", band_counts)
print("class balance via bincount:", np.bincount(y), "-> fraud share", f"{y.mean():.1%}")
for name in ("small", "medium", "large"):
    print(f"   fraud rate in {name:6s}: {y[band == name].mean():.1%}")

# ---------------------------------------------------- 7. reshape / stack / trig
print("=" * 70, "\n7. RESHAPE, STACK, CYCLIC HOUR ENCODING")
print("reshape (-1, 1):", amount[:4].reshape(-1, 1).shape, "| flatten back:", amount[:4].reshape(-1, 1).ravel().shape)
hour_sin = np.sin(2 * np.pi * hour / 24)             # 23:00 and 00:00 end up close together
hour_cos = np.cos(2 * np.pi * hour / 24)
cyc = np.column_stack([hour_sin, hour_cos])
print("hour 23 vs 0 in raw form differ by 23; on the circle they are neighbours:")
print("   (sin,cos) hour 23:", cyc[hour == 23][0].round(3), " hour 0:", cyc[hour == 0][0].round(3))

# -------------------------------------------------------------- 8. randomness
print("=" * 70, "\n8. SEEDED RANDOMNESS (reproducible experiments)")
rng1, rng2 = np.random.default_rng(42), np.random.default_rng(42)
print("same seed, same numbers:", np.array_equal(rng1.integers(0, 100, 5), rng2.integers(0, 100, 5)))
idx = np.random.default_rng(42).permutation(len(X))  # manual 80/20 split with NumPy
cut = int(0.8 * len(X))
tr, te = idx[:cut], idx[cut:]
print(f"manual split: train={len(tr)} test={len(te)} | fraud share train={y[tr].mean():.3f} test={y[te].mean():.3f}")
print("(sklearn's stratify=y keeps these two shares equal; a plain shuffle only approximates it)")

# ------------------------------------------------ 9. correlation / linear algebra
print("=" * 70, "\n9. CORRELATION & LINEAR ALGEBRA")
r = np.corrcoef(amount, y)[0, 1]
print(f"corr(amount, is_fraud) = {r:.3f}")
corr = np.corrcoef(Z, rowvar=False)                  # n_features x n_features correlation matrix
print("correlation matrix shape:", corr.shape, "| symmetric:", np.allclose(corr, corr.T))
eigvals = np.linalg.eigvalsh(corr)[::-1]
print("eigenvalues (largest 3):", eigvals[:3].round(2),
      f"-> top-3 components hold {eigvals[:3].sum() / eigvals.sum():.0%} of variance (idea behind PCA)")
