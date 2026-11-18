# Viva / defence cross-questions — UPI Fraud Detection

Every number below comes from running the scripts in this project. If you re-run and see small differences,
trust your own output, but know the source of each figure (script noted in brackets).

---

## A. Dataset choice

**Q1. You were given four datasets. Why did you model only one?**
I ran the same baseline (Random Forest, class-weighted) on each labelled dataset [00]. `fraud_dataset.csv` gave ROC-AUC 0.97 and PR-AUC 0.95.
`upi_transactions_2024.csv` gave AUC 0.55 (fraud rate 0.19%, PR-AUC 0.002), and `upi_data_new1.xlsx` gave AUC 0.56, so in both the features barely
carry information about the label. A supervised model cannot learn what isn't there. `upi_fraud_india_dataset.csv` has only fraud rows (1,000 of 1,000), so
there is no legitimate class to compare against.

**Q2. Why not merge all the files into one big dataset?**
They share no usable columns (only `timestamp`, which is malformed in `fraud_dataset.csv`). Their fraud rates are 17% vs 0.19%, and their amount scales
differ, so a merged model would mostly learn which file a row came from. Stacking would also add noise, not signal. Instead each file has a role:
modelling, EDA, context. They are joined only where a real key exists: **state**, in the merge in script 02.

**Q3. So what did you actually do with the other files?**
`upi_transactions_2024.csv` powers the volume and behaviour charts (monthly trend, states, devices, weekday × hour heatmap) [03]. `upi_fraud_india_dataset.csv`
gives the fraud-type mix, victim age vs recovery, and, merged on state with the 2024 volume, an illustrative reported-cases-per-100k-transactions view [02, G].
Only 10 of the 16 states match, so I used an inner join and reported the 6 unmatched states.

**Q4. The data is synthetic. Doesn't that make your results meaningless?**
It limits what I can claim. The results show that the pipeline works and that the methodology is sound; they do not show 97% accuracy on real UPI traffic.
Signs of synthetic origin: each fraud "recipe" leaves a signature (e.g. every `unusual_device_flag = 1` row is fraud), names are Western, and coordinates are random.
I say this up front and would retrain on real bank data before any deployment.

**Q5. Why was `upi_data_new1.xlsx` rejected?**
Columns are label-encoded integers (`category`, `state`, `zip`, `upi_number`), some amounts are negative, all data is from 2022, and a baseline model got AUC 0.56
(barely above a coin flip). Fraud and non-fraud rows have almost identical means for amount, hour and age.

---

## B. Data leakage and feature selection (the question most likely to be asked)

**Q6. Your first run gave 100% — why doesn't the final model?**
Because the raw dataset leaks the label. A Random Forest on all columns scores AUC 1.000 [04]. I tested for leakage instead of guessing:
* `receiver_account_age` alone has AUC 0.993 (fraud receivers have account age 0, legitimate median 136 days).
* `handle_verification_status`: "unverified" appears in 100% of fraud rows and never in legitimate rows: it is the label under another name.
* `merchant_category_code = 'unknown'`: 2,914 rows, all fraud, holding 64% of all fraud.
* `unusual_location_flag` is an exact duplicate of `unusual_ip_flag`.

**Q7. After removing those, the score was still 1.000. What did you do?**
Correct: the ladder is 1.000 (all columns) → 1.000 (flagged columns removed) → 0.965 (final set) [04]. The remaining `handle_*`, `request_*` and
screen-mirroring columns are *scenario markers*: each is filled by only one synthetic fraud recipe, so a model memorises the recipe instead of learning
general fraud behaviour. I kept continuous behavioural signals a payment app could observe at transaction time.

**Q8. Isn't that cherry-picking features until the score looks reasonable?**
It is a judgement call and I say so. What makes it defensible: (1) the leakage rules are stated and measurable, not chosen after seeing model scores;
(2) I show all three rungs of the ladder so the effect of the choice is visible; (3) the final score is *lower*, which is the opposite of cherry-picking for a good number.
A sceptic can rerun with the full set and will see 1.000, which itself is the evidence that the raw data is too easy.

**Q9. Two features are 100% correlated, and several are 0.8-0.9. Does that matter?**
Yes, so I dropped the exact duplicate (`unusual_location_flag`). For the correlated group (auth attempts, failed transactions, velocity, OTP requests: 0.82-0.91)
tree models and SVM are robust, but Logistic Regression coefficients become unstable because the features share credit. I therefore only read LR odds ratios as
rough direction, not precise effects.

---

## C. Preprocessing

**Q10. Why stratified splitting?** Fraud is 17.2% of rows. A random split can shift that share; `stratify=y` keeps train/test at 17.2% each [04], so metrics are comparable.

**Q11. Why fit the scaler on train only?** Fitting on all data lets test-set statistics influence training (leakage). The scaler and encoder sit inside a `Pipeline`, so they are fitted on train and only applied to test. Here the gap is tiny (mean 4,865 vs 4,861), but the principle matters.

**Q12. You kept the outliers. Why?** By the IQR rule 1,477 payments (5.6%) are outliers, and 98.1% of them are fraud [02]. Deleting them would delete the signal. I used log scale for plots and scaling for linear models instead.

**Q13. Label Encoding or One-Hot?** Label Encoding assigns alphabetical integers, implying an order (Delhi < Gujarat < ...) that doesn't exist. That misleads LR, SVM and K-Means, but is harmless for trees. One-Hot avoids the false order. My two categorical features are binary (`session_source`, `pin_entry_method`), so One-Hot gives two clean columns [04].

**Q14. Do you scale for Random Forest?** Not needed, since trees split on order, not magnitude. I use one shared preprocessor for all four models for simplicity; it is harmless for trees and required for LR, SVM and K-Means.

**Q15. How did you handle the class imbalance?** `class_weight='balanced'` (or `balanced_subsample` for RF), which penalises missed fraud more heavily, plus stratified splits and imbalance-aware metrics. I did not use SMOTE: with 17% fraud the imbalance is moderate, and synthetic oversampling on already-synthetic data adds another layer of artificiality.

---

## D. K-Means (Module 10)

**Q16. You have labels. Isn't your unsupervised step secretly supervised?**
No. K-Means never sees `is_fraud`; features are scaled numeric behaviour only. I look at the label *after* clustering to grade the result (external validation), the same way one would check whether customer segments line up with churn.

**Q17. How did you choose k?** Elbow plus silhouette on a 5,000-row sample (the full calculation is O(n²)). Silhouette peaked at k=2 (0.718) [05].

**Q18. What did K-Means find?** At k=2, one small cluster of 733 transactions (2.8%) is **100% fraud**: many authentication attempts (~4), failed payments (~2), very fast PIN entry (0.15 vs 1.22). Ranking all transactions by distance to their centroid, the top 10% contains 99.2% fraud [05].

**Q19. Does that mean K-Means detects fraud well?** Be honest here: no. The 733-row cluster holds only 16% of all fraud. The rest looks "normal" in cluster terms. At k=3 a second all-fraud group splits off and near-pure fraud clusters cover 48% of fraud (62% at k=5). Silhouette is high at k=2 *because* one small, extreme group is well separated; it doesn't tell you the clusters cover all fraud. Unsupervised learning finds unusual behaviour; supervised learning is what catches the subtle fraud.

**Q20. Limitations of K-Means?** It assumes roughly spherical, similar-sized clusters, is sensitive to scaling and outliers, needs k in advance, and is a poor fit for categorical features. The PCA plot shows only ~48% of the variance in 2-D, so the picture is a squashed view.

---

## E. Supervised models and metrics

**Q21. 97.7% accuracy: is that good?** Not by itself. A model that predicts "legitimate" for everything gets **82.8% accuracy and catches 0 fraud** [06]. That is why I report precision, recall, F1, ROC-AUC and PR-AUC, and show the confusion matrix.

**Q22. Why does recall matter more than accuracy here?** A missed fraud costs real money; a false alarm costs a moment of friction (an OTP, a call). Recall answers "of all fraud, how much did we catch?" Precision answers "of everything we flagged, how much was really fraud?" The threshold decides the balance.

**Q23. Your recall is 88%, so you miss 12% of fraud. Acceptable?** For a demo, yes; for production it needs work. Lowering the threshold to 0.2 lifts recall only to 0.904 (87 missed vs 110) at the cost of 81 false alarms vs 14 [06]. The ceiling exists because about 8% of fraud rows (380 of 4,545) show none of the trigger signals in this data (unusual device/IP/amount, failed or repeated authentication, time pressure), and some more sit close to legitimate behaviour. More informative features (real receiver history, device intelligence, graph features) are the way forward, not a cleverer threshold.

**Q24. Why did you choose Random Forest?** By cross-validated F1 on the training set (RF 0.929 ± 0.004; SVM 0.923; LR 0.918; DT 0.906), *not* by test score, so the test set stayed untouched for the final estimate. Differences between LR, RF and SVM are small (test F1 0.921-0.928), so RF wins on a combination of F1, probability outputs (needed for the app), and having only 14 false alarms. The SVM has the best precision (0.996, only 3 false alarms) but lower recall and no native probabilities.

**Q25. Could you have overfit?** Checks: 5-fold CV standard deviation is ±0.004-0.007; CV F1 (0.929) matches test F1 (0.928); the Decision Tree is depth-limited (max_depth=6, min_samples_leaf=20); the RF uses min_samples_leaf=2 and 300 trees.

**Q26. Did you tune on the test set?** No. Models were compared with CV on the training set; the test set was used once for the final numbers, and the threshold is left at the default 0.5. The threshold table is shown for discussion only.

**Q27. Why these four algorithms?** They span the syllabus and different inductive biases: LR (linear, interpretable), DT (rules, interpretable), RF (ensemble, robust, low variance), SVM (margin-based, non-linear via RBF kernel). All four land at F1 0.91-0.93, which suggests the ceiling is set by the *data*, not the algorithm.

**Q28. What does the model say drives fraud?** RF importance: amount (0.27), time-pressure indicators (0.22), amount vs sender history (0.10), input timing consistency (0.09), PIN entry speed (0.06). LR odds ratios agree in direction (time pressure ×19 and amount ×16 per standard deviation).

**Q29. Is a large amount always fraud?** No, and the model must not be read that way. In this synthetic data payments of ₹10,000 or more are ~99.6% fraud (1,292 rows) [01], so the model leans heavily on amount. A real system would see many legitimate large payments. That is a known artefact of the simulation.

**Q30. Why not deep learning?** 26k rows with 16 tabular features is a regime where tree ensembles typically match or beat neural nets, and they train in seconds and are easier to explain. Deep learning would add complexity without clear benefit here.

---

## F. Flask app and deployment

**Q31. What does the app do?** It loads the saved pipeline (`models/fraud_model.joblib`), so the same preprocessing used in training is applied to the form input, and returns a fraud probability and verdict. Untouched fields default to the typical legitimate value. It also shows which single inputs push the score up (a counterfactual: "how far would the score drop if this input were typical?").

**Q32. How do you know it works?** Tested through Flask's test client and a live server: default form → 0.1% (safe); ₹300 at 2 PM → 0.5% (safe); ₹95,000 at 2 AM via link with pasted PIN → 100% (fraud suspected); malformed input (letters, hour 31, NaN, unknown category) → clear error messages, no crash.

**Q33. Why isn't this production-ready?** No authentication, no logging or monitoring, trained on simulated data, a single model version, no drift detection, and no latency or load testing. Real deployment would need those plus a feedback loop from analyst decisions.

**Q34. Concept drift?** Fraudsters adapt, so model performance decays. Production systems monitor precision/recall on confirmed cases and retrain regularly. This project uses a static random split; a real evaluation would use a time-based split.

---

## G. Curveballs

**Q35. What would you do differently with more time?** Get real (or higher-quality) data; use time-based splits; add receiver-side and device-history features legitimately; try gradient boosting; calibrate probabilities; add SHAP for explanations; and evaluate cost-sensitively (₹ lost per missed fraud vs ₹ cost per false alarm).

**Q36. Why random_state=42?** Reproducibility: the same split and results every run. 42 has no special meaning; CV standard deviations of ±0.004-0.007 show results don't hinge on that one seed.

**Q37. Fairness or privacy concerns?** Blocking legitimate users has a cost, and features like location or device can correlate with region or income. A production system needs bias audits and clear appeal paths. The data here contains no real personal information.
