from pptx import Presentation
from pptx.util import Pt
from lxml import etree

prs = Presentation('/Users/avijitaditya/Desktop/PaySafe_India_SIH2025.pptx')

notes = [

# SLIDE 1 — TITLE
"""Good [morning/afternoon], respected judges and guests.

I am [Your Name], and on behalf of Team PaySafe India, I welcome you to our Smart India Hackathon 2025 presentation.

The problem we are solving is one of India's fastest-growing financial threats — UPI payment fraud.
India processes over 13 billion UPI transactions every month, and fraudsters are becoming increasingly sophisticated.

PaySafe India is an end-to-end Artificial Intelligence system that scores every UPI transaction in real time and flags fraud before the payment clears.

We have benchmarked five machine learning algorithms, built a fully automated preprocessing pipeline to prevent data leakage, and deployed the best model as a live Flask web application — all of which we will walk you through today.

Let us begin.""",

# SLIDE 2 — PROBLEM STATEMENT
"""Let me set the context with the scale of the problem.

According to RBI data for FY 2023-24, UPI fraud losses crossed ₹2,537 crore, with over 95,000 fraud cases reported annually.

The core challenge is that traditional rule-based systems — such as blocking transactions above a fixed amount — are too rigid. Fraudsters adapt quickly and bypass these rules.

What we need is a system that learns the BEHAVIOURAL fingerprint of fraud:
- Does the payment come at 2 AM?
- Was the PIN entered suspiciously fast — possibly by a script?
- Has this sender been failing authentication repeatedly?
- Is the transaction amount 8 times their usual spending?

None of these signals alone is conclusive — but together, they paint a picture. That is exactly what machine learning can capture, and that is what PaySafe India does.

Another key challenge we addressed is class imbalance. In our primary dataset, 17.2% of transactions are fraud — but in real UPI data, fraud can be as rare as 0.19%. We handle this through class-weighted training, ensuring the model never ignores the minority fraud class.""",

# SLIDE 3 — PROJECT INTRODUCTION
"""PaySafe India is a complete, production-ready fraud detection pipeline.

Let me highlight what makes this project stand out:

First, we evaluated FOUR different UPI datasets before selecting one for modelling. This is critical — not every dataset with a fraud label actually has predictive signal in its features. We measured baseline ROC-AUC on each dataset using a Random Forest, and only fraud_dataset.csv with 26,393 transactions had genuine signal (AUC = 0.969 versus ~0.55 for others).

Second, we ran a rigorous leakage audit. Synthetic datasets often contain features that directly reveal the label. We identified and removed such columns systematically using three rules — single-feature AUC threshold, 100%-fraud category coverage, and duplicate column detection.

Third, we deployed the final model as a Flask web application. A user can enter any transaction's details and receive:
- A fraud probability score (0–100%)
- A risk band: Low, Medium, or High
- An explanation of WHICH fields are driving the score up

Our best model — Random Forest with 300 trees — achieves 98.3% Precision and 96.9% ROC-AUC on 5,279 unseen test transactions.""",

# SLIDE 4 — OBJECTIVES
"""Our project is built around six concrete, measurable objectives.

Objective 1 is Real-Time Fraud Detection. Our Flask API scores a transaction in under 50 milliseconds by running the pre-trained scikit-learn pipeline in memory.

Objective 2 is Rigorous Dataset Evaluation. We did not just pick the largest dataset — we picked the one where features actually predict fraud, proven by baseline AUC comparison.

Objective 3 is Leakage-Free Feature Engineering. Data leakage is the silent killer of ML projects. We implemented three automated rules to detect and remove leaky columns before any model sees the data.

Objective 4 is Multi-Algorithm Benchmarking. We trained K-Means, Logistic Regression, Decision Tree, Random Forest, and SVM — comparing them fairly using 5-fold cross-validation on training data only.

Objective 5 is Fraud-Aware Metrics. Accuracy is completely misleading for imbalanced fraud data. A model that flags everything as legitimate scores 82.8% accuracy with zero fraud caught. We always report Precision, Recall, F1, and ROC-AUC.

Objective 6 is Explainability. Every prediction comes with a counterfactual driver analysis — telling the user WHICH inputs pushed the score above the fraud threshold.""",

# SLIDE 5 — SCOPE & BENEFITS
"""Let me now explain where PaySafe India can be deployed and what value it delivers.

On the implementation side, our system is designed to integrate with:
- UPI platforms like PhonePe, Google Pay, and BHIM via our REST API
- Bank fraud monitoring dashboards as a first-pass screening tool
- Real-time transaction gateways where our /api/predict endpoint returns a JSON response in milliseconds
- Regulatory systems where model cards and explainability reports can satisfy RBI compliance requirements

The benefits are significant for all stakeholders:

For banks: Fewer missed fraud cases means lower financial losses. Our Random Forest misses only 110 fraud transactions out of ~900 in the test set — and raises only 14 false alarms.

For customers: False declines — where a legitimate payment is blocked — destroy trust. Our system's 98.3% precision means only 14 legitimate payments were unnecessarily blocked in 5,279 test transactions.

For regulators: Every prediction is explainable. We can tell RBI exactly which behavioural signals triggered a fraud alert.

For developers: Our pipeline is modular. New features can be added to config.py and the entire pipeline retrains automatically.""",

# SLIDE 6 — DATASETS
"""We started with four UPI datasets and evaluated each systematically.

The evaluation methodology was simple but rigorous: train a 100-tree Random Forest on 80% of each labelled dataset, measure ROC-AUC on the held-out 20%. An AUC of 0.5 means the features carry no signal — equivalent to a coin flip. AUC of 1.0 means perfect separation.

Results:
- fraud_dataset.csv: AUC = 0.969 — SELECTED for modelling
- upi_transactions_2024.csv: AUC ≈ 0.55 — used for EDA and visualisation only, not modelling
- upi_data_new1.xlsx: AUC ≈ 0.56 — REJECTED; uses anonymised codes with no real signal
- upi_fraud_india_dataset.csv: Cannot be classified — every single row is a fraud case, so there is no legitimate class to learn from

This is a critical point for judges: selecting the wrong dataset would have given us a model that looks perfect in the lab but fails completely on real data. Dataset selection is not a trivial step — it is a scientific decision backed by evidence.

The three datasets we use serve different roles: fraud_dataset.csv for all machine learning, upi_transactions_2024.csv for exploratory analysis and state-level visualisations, and upi_fraud_india_dataset.csv for fraud-type context in the EDA.""",

# SLIDE 7 — SYSTEM ARCHITECTURE
"""Let me walk you through how PaySafe India works from end to end.

The top diagram shows the training pipeline:
Raw data enters scripts 00 through 02 for EDA and cleaning. Scripts 02 through 04 handle feature engineering and the leakage audit. Scripts 05 and 06 train all five algorithms and select the best. Script 06 saves the final pipeline as fraud_model.joblib and a JSON metadata file. The Flask app then loads these at startup.

The bottom diagram shows the live web application flow:
A user opens http://127.0.0.1:5000 in their browser. They fill in transaction details — amount, time of day, authentication attempts, device flags, and so on. On clicking 'Check Transaction', the browser sends a POST request to the Flask route. Flask calls parse() to validate inputs, then assess() to score the transaction. The predict_proba method of the Random Forest pipeline returns a fraud probability. If it is 0.5 or higher, the transaction is flagged. The result page shows the probability, a colour-coded risk band, and up to 3 counterfactual driver explanations.

The REST API at /api/predict accepts JSON and returns the same result — making integration with banking systems straightforward.""",

# SLIDE 8 — K-MEANS
"""Now let us go through each algorithm, starting with K-Means — our unsupervised approach.

The key design decision here is that K-Means does NOT see the fraud label during training. It only sees the 14 scaled numeric behavioural features. We use labels only AFTER clustering, purely to validate that the clusters align with fraud.

Mathematically, K-Means minimises the Within-Cluster Sum of Squares — the total squared distance from each point to its assigned cluster centroid. The algorithm alternates between assigning each transaction to its nearest centroid and recomputing centroids as the mean of assigned points.

To choose the optimal number of clusters k, we used two methods:
- The Elbow Method: plot inertia (WCSS) versus k and look for the bend
- The Silhouette Score: measures how tight clusters are internally and how separated they are from each other. Scores range from -1 to 1; higher is better.

Results: k=3 gave the best silhouette. One cluster of 733 transactions turned out to be 100% fraud. The distance-to-centroid anomaly score is powerful: flagging the top 10% of outliers by distance catches 99% precision for fraud — with zero labels used during detection.

The important caveat: K-Means only isolated ONE tight fraud pattern. Roughly 40% of fraud is scattered across the 'legitimate' cluster. This is why we still need supervised learning — K-Means is a powerful complement, not a replacement.""",

# SLIDE 9 — LOGISTIC REGRESSION
"""Logistic Regression is our linear probabilistic baseline.

The sigmoid function maps any real-valued linear combination of features to a probability between 0 and 1. The decision boundary is a hyperplane in feature space.

We train it by minimising Binary Cross-Entropy loss using the L-BFGS optimiser with up to 2,000 iterations to ensure convergence on our high-dimensional feature space.

Because fraud is the minority class, we use class_weight='balanced', which automatically up-weights fraud samples during loss computation. The weight for each class is n / (2 × n_class), where n is total samples and n_class is samples in that class.

Interpretability is a key strength of Logistic Regression: we can compute Odds Ratios by exponentiating the coefficients. Our top fraud predictors by odds ratio are authentication_attempts (OR ≈ 4.2), failed_transaction_count (OR ≈ 3.8), and unusual_device_flag (OR ≈ 3.1). This means a transaction with abnormally high authentication attempts has 4.2 times the odds of being fraud, holding other features constant.

Results: 96.5% ROC-AUC and 92.1% F1 — strong performance with just 32 false alarms. The model is fast, interpretable, and robust — making it an excellent secondary validator.""",

# SLIDE 10 — DECISION TREE
"""Decision Trees split the feature space using threshold rules chosen to maximise Information Gain — measured by the reduction in Gini Impurity.

Gini Impurity at a node equals 1 minus the sum of squared class probabilities. A pure node (all one class) has Gini = 0. The most mixed node (50-50 split) has Gini = 0.5.

At each node, the algorithm evaluates every possible threshold for every feature and picks the one that maximally reduces Gini. This creates human-readable if-else rules.

Our hyperparameters: max_depth=6 prevents overfitting by limiting tree depth, and min_samples_leaf=20 ensures each leaf represents at least 20 transactions — avoiding noisy micro-rules.

An example top-level rule from our trained tree:
If amount (z-score) ≤ 1.2 AND authentication_attempts (z-score) ≤ 0.8 → Legitimate
If authentication_attempts > 0.8 → Fraud

This kind of rule is extremely valuable for regulatory compliance — a human investigator can read and audit it.

Results: 96.2% ROC-AUC and 90.8% F1. Notably, the Decision Tree misses the fewest fraud cases (99 vs 105 for LR and 110 for RF), making it attractive when recall is the absolute priority.""",

# SLIDE 11 — RANDOM FOREST
"""Random Forest is our deployed model — and the winner of our 5-fold cross-validation comparison.

It is an ensemble of 300 Decision Trees, each trained on a bootstrap sample of the training data with random feature subsets at each split. This combination of bagging and feature randomness dramatically reduces variance compared to a single tree.

The final fraud probability is the average of predict_proba across all 300 trees. This soft voting makes the output well-calibrated and allows threshold tuning.

We use class_weight='balanced_subsample', which recomputes class weights per bootstrap sample — ensuring the minority fraud class is appropriately weighted even within each resampled tree.

Feature Importance via Mean Decrease in Impurity: the top features are amount, transaction_amount_vs_sender_history, authentication_attempts, unusual_device_flag, and failed_transaction_count.

Why was Random Forest selected over SVM despite SVM having higher precision?
- Random Forest has the highest cross-validated F1: 0.929 ± 0.004 versus 0.923 for SVM
- Random Forest outputs predict_proba, enabling threshold tuning — SVM by default does not
- Random Forest has only 14 false alarms — the fewest of any model with probability output
- It is robust to correlated features and outliers, which are common in financial data

The model was selected by CV score, NOT by test score — ensuring no overfitting to the test set in our selection decision.""",

# SLIDE 12 — SVM
"""Support Vector Machine with the RBF kernel is our highest-precision model.

The core idea: find the hyperplane that maximises the margin — the gap between the nearest points of each class, called support vectors. Maximising this margin improves generalisation.

For non-linearly separable data — which real fraud data certainly is — we use the RBF kernel: K(xᵢ, xⱼ) = exp(−γ ‖xᵢ − xⱼ‖²). This implicitly maps the data to an infinite-dimensional space where a linear separator exists, without ever computing that space explicitly. This is the famous 'kernel trick'.

The soft-margin parameter C = 1.0 controls the trade-off between maximising margin and minimising misclassification. Higher C means fewer training errors but risk of overfitting; lower C gives a wider margin but allows more misclassification.

Results: SVM achieves an extraordinary 99.6% Precision — only 3 false alarms in 5,279 test transactions. This makes it the ideal choice in scenarios where blocking a legitimate payment is extremely costly.

However, SVM missed 122 fraud cases — the most of any model. And without probability calibration (probability=True), it cannot produce fraud probabilities for threshold tuning.

This is why Random Forest was selected for deployment: better recall, probability output, and the highest cross-validated F1.""",

# SLIDE 13 — CODE: CONFIG + UTILS
"""Let us now look at the actual code — starting with the foundation of the entire project.

config.py is the single source of truth for all paths and the feature list. Every script imports from config.py, which means changing a feature requires editing exactly one file — and all scripts automatically pick up the change.

The feature list was carefully curated through the leakage audit in script 04. We kept 14 numeric behavioural features and 2 categorical features:
- Numeric: amount, ratio to sender history, time of day, auth attempts, failed count, velocity, session duration, geographic disparity, PIN speed, OTP frequency, time pressure, input timing consistency, unusual device flag, unusual IP flag
- Categorical: session_source (app vs link) and pin_entry_method (typed vs pasted)

utils.py contains build_preprocessor() — the most important function in the project. It creates a scikit-learn ColumnTransformer that applies:
- For numeric features: median imputation followed by StandardScaler
- For categorical features: most-frequent imputation followed by OneHotEncoder

The critical rule enforced by using a Pipeline: the scaler and encoder are FITTED on training data only, and only TRANSFORMED on test data. This prevents test-set information from leaking into the scaling parameters — a common but subtle mistake that inflates reported metrics.""",

# SLIDE 14 — CODE: KMEANS + SUPERVISED
"""Script 05 handles unsupervised learning. The first line is the most important:
X = StandardScaler().fit_transform(df[NUMERIC_FEATURES])
K-Means is distance-based. If we do not scale, 'amount' in rupees would completely dominate 'authentication_attempts' in counts. Scaling ensures every feature contributes equally.

We systematically test k from 2 to 8 using both inertia and silhouette score. The silhouette score is computed on a 5,000-sample subset for computational efficiency — O(n²) is too slow for 26,000 points.

The anomaly score — distance to the nearest centroid — is our unsupervised fraud signal. No labels were used to compute it.

Script 06 trains all four supervised classifiers inside scikit-learn Pipelines. Each Pipeline chains the ColumnTransformer (prep) with the model. This ensures preprocessing is always consistent between training and inference.

Model selection uses 5-fold Stratified K-Fold cross-validation on the TRAINING SET ONLY. Stratified means each fold maintains the same 17.2% fraud rate as the full dataset. We score by F1 — the harmonic mean of precision and recall — because both matter for fraud.

The final three lines save the complete pipeline — including all preprocessing steps — as a single joblib file. The Flask app loads this file at startup and calls predict_proba directly, with no separate preprocessing step needed.""",

# SLIDE 15 — CODE: FLASK APP
"""The Flask application makes PaySafe India accessible to anyone without needing to run Python.

At startup, app.py loads the saved Random Forest pipeline and the JSON metadata file containing the feature list, category options, legitimate medians, and threshold.

The score() function is remarkably simple: it wraps the input dictionary in a single-row DataFrame, reorders columns to match training order, and calls model.predict_proba(). One line returns the fraud probability.

The drivers() function implements counterfactual explanation: for each input field, it asks 'what would the score be if this field were typical for a legitimate payment?' If replacing this one field with its typical value drops the fraud score by 2 percentage points or more, that field is flagged as a driver. The top 3 drivers are returned.

The index() route handles both GET (showing the form) and POST (computing the score). The assess() function packages the probability, band, and drivers into a single dictionary that the Jinja2 template renders.

The /api/predict endpoint enables programmatic integration: any banking system can POST a JSON payload with transaction fields and receive a structured JSON response with probability, band, and drivers.

This architecture means the same model, same preprocessing, and same threshold are used whether the request comes from the web UI or the API.""",

# SLIDE 16 — CODE: LEAKAGE AUDIT
"""Data leakage is the most dangerous pitfall in machine learning for fraud detection. A leaky model looks perfect in the lab and fails completely in production.

Script 04 implements three automated leakage detection rules:

Rule 1: Single-feature AUC threshold. If one numeric feature alone achieves ROC-AUC ≥ 0.94, it is too closely correlated with the label to be a fair feature. We found receiver_account_age and receiver_transaction_history triggered this rule.

Rule 2: Category coverage. If a single category value is 100% fraud AND contains ≥ 50% of all fraud rows, that category is essentially a fraud label in disguise. This caught merchant_category_code and handle_verification_status.

Rule 3: Exact duplicate columns. Duplicate features add no information but waste model capacity and confuse importance scores.

The Accuracy Ladder shows the dramatic impact:
- L1 with all columns: AUC = 1.000 — perfect, but for the wrong reasons
- L2 minus flagged columns: AUC = 1.000 — still perfect because 'scenario marker' columns remain
- L3 compact behavioural set: AUC = 0.965 — realistic performance on genuinely predictive features

This drop from 1.000 to 0.965 is intentional and honest. We chose L3 knowing the score is lower, because a model that actually generalises to real UPI fraud is infinitely more valuable than one that memorises synthetic labels.""",

# SLIDE 17 — MODEL COMPARISON
"""Here is the definitive head-to-head comparison of all four classifiers on 5,279 unseen test transactions.

Starting with the baseline: a dummy model that predicts every transaction as legitimate scores 82.8% accuracy with 0% recall — it catches zero fraud. This is why we never quote accuracy alone.

Looking at the table:
- Random Forest achieves the highest ROC-AUC at 96.9% and the lowest false alarm rate among probability-output models — only 14 legitimate payments incorrectly blocked
- Logistic Regression is a strong second at 96.5% AUC with just 32 false alarms — a great interpretable alternative
- Decision Tree catches the fewest fraud cases missed (99 FN) — best raw recall — at the cost of 65 false alarms
- SVM has the fewest false alarms of all (just 3!) and highest precision (99.6%) but misses the most fraud cases (122)

The selection criterion: highest cross-validated F1 among models that output predict_proba. This excludes SVM (no probabilities by default) and points to Random Forest at CV F1 = 0.929.

CV F1 is the honest metric because it was computed on training data in cross-validation — the test set was never used to make this decision. This prevents the subtle overfitting that occurs when you select a model based on test performance.""",

# SLIDE 18 — FUTURE SCOPE
"""PaySafe India is a solid foundation, and we have a clear vision for making it production-grade.

Eight enhancement directions:

1. Deep Learning with LSTM or Transformer models: fraud patterns are sequential — a series of small transactions before a large fraud payment. Sequence models can capture this temporal structure that tabular models miss.

2. Real-time stream processing with Apache Kafka and Spark: our current Flask app handles one transaction at a time. A production system needs to handle thousands of transactions per second with millisecond latency.

3. Federated Learning: banks cannot share raw customer transaction data with each other due to privacy laws. Federated learning trains models across institutions without centralising data — improving detection while preserving privacy.

4. Graph Neural Networks: fraud often involves rings of colluding accounts — money mules, shell accounts, and chained transfers. GNNs model the account-to-account transaction network and can detect these coordinated fraud patterns.

5. AutoML and Continuous Retraining: fraud patterns evolve monthly. An automated pipeline that detects model drift (via data distribution shift metrics) and retrains on new labelled data keeps the system current.

6. Mobile SDK: embedding PaySafe scoring directly in mobile banking apps at the device level, with on-device inference for the lowest possible latency.

7. Multilingual Explainability: fraud investigators across India speak Hindi, Tamil, Telugu, Bengali. Generating driver explanations in regional languages makes the system accessible at scale.

8. RBI Regulatory Compliance: producing formal model cards, bias audits, and explainability reports aligned with the RBI's guidelines for AI/ML in banking.""",

# SLIDE 19 — THANK YOU
"""To summarise what Team PaySafe India has built:

A complete, end-to-end AI-powered UPI fraud detection system that:
- Evaluated 4 datasets scientifically and selected the one with genuine predictive signal
- Removed data leakage systematically using automated three-rule audit
- Benchmarked 5 algorithms — K-Means, Logistic Regression, Decision Tree, Random Forest, and SVM
- Selected Random Forest through cross-validation — not test score — for deployment
- Achieved 96.9% ROC-AUC and 98.3% Precision on 5,279 unseen transactions
- Deployed as a live Flask web application with real-time scoring, counterfactual explanations, and a REST API

PaySafe India is not just a student project — it is a deployable prototype with a clear path to production integration with India's UPI infrastructure.

We believe AI-powered fraud detection is not just a technical challenge — it is a social responsibility. Every fraudulent transaction that goes undetected hurts a real person. PaySafe India exists to prevent that.

Thank you for your time and attention. We welcome your questions.""",
]

def add_notes_to_slide(slide, note_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = note_text

for i, (slide, note) in enumerate(zip(prs.slides, notes)):
    add_notes_to_slide(slide, note.strip())
    print(f"  Added notes to Slide {i+1}")

prs.save('/Users/avijitaditya/Desktop/PaySafe_India_SIH2025.pptx')
print("\nSaved with speaker notes: /Users/avijitaditya/Desktop/PaySafe_India_SIH2025.pptx")
