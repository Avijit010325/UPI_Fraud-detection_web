# ================================================================
# PaySafe India - UPI Fraud Detection (Simple Version)
# Covers Modules 2,3,4,5,6,7,8,9,10 in one linear flow
# ================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


# ================================================================
# 1. LOAD DATASET
# ================================================================
# If you have the real Kaggle CSV, use:
# df = pd.read_csv('upi_transactions.csv')

# Sample dataset generator (replace with real CSV when you have it)
np.random.seed(42)
n = 1000
df = pd.DataFrame({
    'amount': np.concatenate([np.random.uniform(100, 50000, 950),
                               np.random.uniform(40000, 200000, 50)]),
    'hour': np.random.randint(0, 24, n),
    'day': np.random.randint(0, 7, n),
    'bank': np.random.choice(['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB'], n),
    'state': np.random.choice(['Maharashtra', 'Karnataka', 'Delhi',
                                'Tamil Nadu', 'West Bengal'], n),
    'merchant': np.random.choice(['Food', 'Grocery', 'Fuel',
                                   'Healthcare', 'Entertainment'], n),
    'device': np.random.choice(['Android', 'iOS', 'Web'], n),
    'fraud': np.concatenate([np.zeros(950), np.ones(50)]).astype(int)
})


# ================================================================
# 2. CREATE DATAFRAME - BASIC EXPLORATION (Module 3)
# ================================================================
print("df.head()")
print(df.head())

print("\ndf.info()")
print(df.info())

print("\ndf.columns")
print(df.columns)

print("\ndf.shape")
print(df.shape)

print("\ndf.describe()")
print(df.describe())


# ================================================================
# 3. NUMPY BASICS (Module 2)
# ================================================================
amounts = df['amount'].values          # convert column to numpy array
print("\nAmount array shape:", amounts.shape)
print("Mean amount:", np.mean(amounts))
print("Median amount:", np.median(amounts))
print("Std amount:", np.std(amounts))
print("Max amount:", np.max(amounts))
print("Min amount:", np.min(amounts))


# ================================================================
# 4. DATA CLEANING (Module 4)
# ================================================================
print("\nMissing values:\n", df.isnull().sum())

# fillna example (works even if no nulls exist)
df['amount'] = df['amount'].fillna(df['amount'].median())

# drop duplicates
df = df.drop_duplicates()

# IQR outlier detection
Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = df[(df['amount'] < lower) | (df['amount'] > upper)]
print("\nOutliers found:", len(outliers))

# feature engineering
df['is_weekend'] = (df['day'] >= 5).astype(int)
df['is_night'] = ((df['hour'] >= 23) | (df['hour'] <= 4)).astype(int)


# ================================================================
# 5. VISUALIZATION (Module 5)
# ================================================================

# Bar chart - fraud rate by state
plt.figure(figsize=(8, 4))
df.groupby('state')['fraud'].mean().plot(kind='bar', color='tomato')
plt.title('Fraud Rate by State')
plt.ylabel('Fraud Rate')
plt.tight_layout()
plt.savefig('chart_bar_state.png')
plt.close()

# Histogram - amount distribution
plt.figure(figsize=(8, 4))
plt.hist(df['amount'], bins=40, color='skyblue')
plt.title('Amount Distribution')
plt.xlabel('Amount')
plt.tight_layout()
plt.savefig('chart_histogram.png')
plt.close()

# Pie chart - fraud vs genuine
plt.figure(figsize=(5, 5))
df['fraud'].value_counts().plot(kind='pie', autopct='%1.1f%%',
                                 labels=['Genuine', 'Fraud'],
                                 colors=['green', 'red'])
plt.title('Fraud vs Genuine')
plt.ylabel('')
plt.tight_layout()
plt.savefig('chart_pie.png')
plt.close()

# Scatter plot - amount vs hour
plt.figure(figsize=(8, 5))
plt.scatter(df['hour'], df['amount'], c=df['fraud'], cmap='coolwarm', alpha=0.5)
plt.title('Amount vs Hour (colored by fraud)')
plt.xlabel('Hour')
plt.ylabel('Amount')
plt.tight_layout()
plt.savefig('chart_scatter.png')
plt.close()

# Seaborn count plot
plt.figure(figsize=(5, 4))
sns.countplot(data=df, x='fraud')
plt.title('Class Count')
plt.tight_layout()
plt.savefig('chart_countplot.png')
plt.close()

# Seaborn box plot
plt.figure(figsize=(6, 4))
sns.boxplot(data=df, x='fraud', y='amount')
plt.title('Amount by Fraud Class')
plt.tight_layout()
plt.savefig('chart_boxplot.png')
plt.close()

# Seaborn violin plot
plt.figure(figsize=(6, 4))
sns.violinplot(data=df, x='fraud', y='amount')
plt.title('Amount Distribution Shape')
plt.tight_layout()
plt.savefig('chart_violin.png')
plt.close()

# Seaborn correlation heatmap
plt.figure(figsize=(6, 5))
num_cols = ['amount', 'hour', 'day', 'is_weekend', 'is_night', 'fraud']
sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('chart_heatmap.png')
plt.close()

print("\nAll charts saved as PNG files")


# ================================================================
# 6. ENCODING & PREPROCESSING (Module 6)
# ================================================================
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# Label Encoding
le_bank = LabelEncoder()
df['bank'] = le_bank.fit_transform(df['bank'])

le_device = LabelEncoder()
df['device'] = le_device.fit_transform(df['device'])

# One-Hot Encoding
df = pd.get_dummies(df, columns=['state', 'merchant'], drop_first=True)

# convert bool columns to int
bool_cols = df.select_dtypes(include='bool').columns
df[bool_cols] = df[bool_cols].astype(int)

# X and y
X = df.drop('fraud', axis=1)
y = df['fraud']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nX_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)


# ================================================================
# 7. K-MEANS CLUSTERING - Unsupervised (Module 10)
# ================================================================
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Elbow method
inertias = []
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_train_scaled)
    inertias.append(km.inertia_)

plt.figure(figsize=(7, 4))
plt.plot(range(2, 8), inertias, marker='o')
plt.title('Elbow Method')
plt.xlabel('K')
plt.ylabel('Inertia')
plt.tight_layout()
plt.savefig('chart_elbow.png')
plt.close()

# Train final K-Means with K=4
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
train_clusters = kmeans.fit_predict(X_train_scaled)
test_clusters = kmeans.predict(X_test_scaled)

sil_score = silhouette_score(X_train_scaled, train_clusters)
print("\nSilhouette Score:", sil_score)

# add cluster as new feature
X_train['cluster'] = train_clusters
X_test['cluster'] = test_clusters


# ================================================================
# 8. MODEL TRAINING - Supervised (Module 7, 8, 9)
# ================================================================
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score,
                              recall_score, f1_score, confusion_matrix)

def evaluate(name, y_true, y_pred):
    print(f"\n{name}")
    print("Accuracy :", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred, zero_division=0))
    print("Recall   :", recall_score(y_true, y_pred, zero_division=0))
    print("F1-Score :", f1_score(y_true, y_pred, zero_division=0))

# --- Logistic Regression ---
lr = LogisticRegression(class_weight='balanced', max_iter=1000)
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
evaluate("Logistic Regression", y_test, y_pred_lr)

# --- Decision Tree ---
dt = DecisionTreeClassifier(max_depth=8, class_weight='balanced', random_state=42)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)
evaluate("Decision Tree", y_test, y_pred_dt)

# --- Random Forest ---
rf = RandomForestClassifier(n_estimators=100, max_depth=12,
                             class_weight='balanced', random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
evaluate("Random Forest", y_test, y_pred_rf)

# --- SVM ---
svm = SVC(kernel='rbf', class_weight='balanced', random_state=42)
svm.fit(X_train, y_train)
y_pred_svm = svm.predict(X_test)
evaluate("SVM", y_test, y_pred_svm)


# ================================================================
# 9. CONFUSION MATRIX + FEATURE IMPORTANCE
# ================================================================
cm = confusion_matrix(y_test, y_pred_rf)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Genuine', 'Fraud'],
            yticklabels=['Genuine', 'Fraud'])
plt.title('Confusion Matrix - Random Forest')
plt.tight_layout()
plt.savefig('chart_confusion_matrix.png')
plt.close()

importances = pd.Series(rf.feature_importances_, index=X_train.columns)
importances = importances.sort_values(ascending=False)

plt.figure(figsize=(8, 5))
importances.head(10).plot(kind='barh', color='purple')
plt.title('Feature Importance - Random Forest')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('chart_feature_importance.png')
plt.close()

print("\nTop features:\n", importances.head(5))
print("\nDone. All charts saved. Random Forest is the final model.")
