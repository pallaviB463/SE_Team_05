# Predictive Analytics Evaluation Report

| Item | Value / Notes |
|---|---|
| Model used | Least-squares linear trend on semester SGPA, extrapolated one semester, clipped to 0-10 (no trained ML model) |
| Dataset (source, size, synthetic?) | Synthetic, 300 students x 3 semesters (apas.seed, seed 2026) |
| Train/test split | Time-based hold-out: semesters 1-2 as history, semester 3 as the test target (no model training, so no 80/20 split) |
| Input features | Semester SGPA history (attendance is used for the risk level, not the SGPA forecast) |
| Evaluation method | MAE/RMSE on predicted SGPA; at-risk = SGPA < 6.0: precision, recall, F1, accuracy, confusion matrix |
| Accuracy | 0.863 (at-risk classification); SGPA MAE 0.858, RMSE 1.39 |
| Precision (at-risk) | 0.814 |
| Recall (at-risk) | 0.775 |
| F1 | 0.794 |
| Observed results | 300/300 predictions produced; confusion TP 79, FP 18, FN 23, TN 180; bias 0.071. Students with < 2 semesters get 'insufficient data'. |
| Limitations | Data quality/volume; misclassification risk; decision-support only; synthetic data only; 2-point linear extrapolation |
| Acceptance threshold | None defined in SRS; use only an approved project requirement (raised as review defect DOC-004) |
