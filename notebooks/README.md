# 📒 Notebooks — PaySafe India

This folder contains the Jupyter notebooks for the **PaySafe India UPI Fraud Detection** project.

| Notebook | Description |
|---|---|
| [`PaySafeIndia.ipynb`](./PaySafeIndia.ipynb) | ✅ **Main Project Notebook** — Full 21-cell pipeline: EDA → Preprocessing → K-Means → 4 ML Models → Evaluation → Model Export |
| [`main_analysis.ipynb`](./main_analysis.ipynb) | Extended analysis with additional visualizations and deep-dive cell comments |

## ▶️ How to Run

```bash
# From repo root
pip install -r requirements.txt
jupyter notebook notebooks/PaySafeIndia.ipynb
```

## 🧠 Notebook Structure (PaySafeIndia.ipynb)

| Cell | Module | Description |
|---|---|---|
| C1 | Module 1 | Library imports (NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn) |
| C2 | Module 3 | Load 3 datasets (26,393 / 1,000 / 2,50,000 rows) |
| C3–C5 | Module 3 | EDA: `.head()`, `.info()`, `.describe()`, `.shape` |
| C6 | Module 2 | NumPy statistical analysis (mean ₹4,865 / median ₹3,685 / std ₹5,720) |
| C7 | Module 4 | Data cleaning: missing value audit, duplicate removal |
| C8–C15 | Module 5 | 8 Visualizations: histogram, pie, scatter, countplot, heatmap, boxplot, violinplot, confusion matrix |
| C16 | Module 6 | LabelEncoder + StandardScaler + 80/20 stratified split |
| C17 | Module 10 | K-Means (K=4, Elbow Method, Silhouette Score = 0.2761) |
| C18 | Modules 7–9 | 4 Supervised Models: LR / DT / RF / SVM |
| C19 | Module 9 | Confusion Matrix + Feature Importance |
| C20 | Module 11 | Final Summary + `joblib.dump()` model export |
