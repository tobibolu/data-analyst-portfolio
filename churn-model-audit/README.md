# MTN Nigeria Customer Churn: Leakage-Safe Model Audit

**Author:** Tobi Bolu · [GitHub](https://github.com/tobibolu) · [LinkedIn](https://www.linkedin.com/in/tobibolu/)

## Project overview

This project explores an MTN Nigeria customer-churn dataset, simulates the design of a retention experiment, and audits whether the available data can support pre-churn prediction.

The most important result is methodological. An earlier version reported ROC AUC above 0.92, but that score was invalid because it included `Reasons for Churn`, a post-outcome field, and split repeated records from the same customer across train and test. The rebuilt workflow withdraws that claim, aggregates to customer level, and evaluates only temporally defensible features.

The corrected result is intentionally honest: **the remaining data does not support a useful churn-ranking model**. That finding is more actionable than an inflated metric because it identifies the real next requirement: timestamped behavioural data collected before churn.

## Dataset and prediction grain

- Source: [MTN Nigeria Customer Churn on Kaggle](https://www.kaggle.com/datasets/oluwademiladeadeniyi/mtn-nigeria-customer-churn)
- Source shape: 974 rows
- Unique customers: 496
- Customer-level churn prevalence: 29.4% (146 of 496)
- Prediction unit: one row per `Customer ID`

Multiple source rows belong to the same customer and can contain different plan or device records. The modelling notebook therefore aggregates them before splitting so one person cannot appear in both training and holdout data.

## Repository structure

```text
churn-model-audit/
├── 01_eda_cleaning.ipynb       # Exploration and source-data preparation
├── 02_ab_test_analysis.ipynb   # Simulated retention-experiment design
├── 03_churn_model.ipynb        # Executed leakage-safe model audit
├── app.py                      # Streamlit audit dashboard
├── cleaned_data.csv            # 974 prepared source rows
├── predictions.csv             # 496 exploratory customer scores
├── model_metrics.json          # Machine-readable verified evaluation
└── README.md
```

## Churn-model methodology

### Leakage controls

The model excludes:

- `Customer Churn Status`, the target;
- `Reasons for Churn`, which is known only after churn;
- customer ID and name, which are identifiers rather than behavioural predictors;
- satisfaction and customer-review fields because their collection timing is undocumented.

The remaining customer-level features cover demographics, tenure, modal plan/device, number of plans/devices, and aggregated purchase, revenue, and usage measures.

### Evaluation design

1. Aggregate 974 source rows to 496 unique customers.
2. Create a stratified 75/25 train/holdout split at customer level.
3. Put median imputation, standardisation, one-hot encoding, and logistic regression inside one scikit-learn `Pipeline`/`ColumnTransformer`.
4. Run five-fold stratified cross-validation on the 372 training customers.
5. Select a threshold using out-of-fold training probabilities and an explicit illustrative cost of `5 × false negatives + 1 × false positives`.
6. Evaluate once on 124 untouched holdout customers.

All preprocessing statistics are learned from training folds only. The cost ratio is a transparent scenario, not an MTN financial estimate.

## Verified model results

| Measure | Result | Interpretation |
|---|---:|---|
| Mean five-fold CV ROC AUC | 0.488 ± 0.062 | Approximately no ranking signal |
| Mean five-fold CV average precision | 0.323 ± 0.048 | Close to the 29.4% churn prevalence |
| Untouched-holdout ROC AUC | 0.465 | Worse than random ranking on this sample |
| Untouched-holdout average precision | 0.270 | Below the 29.0% holdout prevalence |
| Cost-selected threshold | 0.11 | Selected from training out-of-fold predictions only |
| Customers flagged on holdout | 124 of 124 | The model cannot prioritise a smaller intervention group |

These metrics mean the model is **not deployment-ready**. The dashboard exposes the audit evidence and labels its full-data scores as exploratory; relative score bands are not validated risk tiers.

## Experiment-design notebook

`02_ab_test_analysis.ipynb` is a simulation, not evidence from a live campaign. It demonstrates:

- hypothesis framing and power analysis;
- control/treatment assignment and simulated binary outcomes;
- chi-squared and two-proportion tests;
- confidence intervals and scenario-based economics.

The simulated example was underpowered: 316 eligible records versus an estimated requirement of roughly 1,505. Its directional lift and ROI calculation must not be presented as a realised business result.

## Dashboard

Run:

```bash
streamlit run app.py
```

The dashboard reads `model_metrics.json`, so its performance numbers come directly from the executed notebook rather than hard-coded claims. It shows:

- cross-validation and untouched-holdout evidence;
- the operational consequence of the illustrative threshold;
- observed-outcome overlap in exploratory scores;
- filterable customer-level demonstration scores;
- a persistent not-deployment-ready warning.

## Reproduce the project

Install the dependencies:

```bash
pip install pandas numpy scikit-learn scipy matplotlib seaborn plotly streamlit jupyter
```

Then execute the notebooks in order:

```bash
jupyter notebook 01_eda_cleaning.ipynb
jupyter notebook 02_ab_test_analysis.ipynb
jupyter notebook 03_churn_model.ipynb
```

The modelling notebook regenerates `predictions.csv` and `model_metrics.json`.

## Recommended next iteration

A credible operational model needs a prediction timestamp and features known before that timestamp, such as recent recharge frequency and trend, failed calls/data sessions, complaint history, local network quality, payment failures, offer exposure, and tenure events. Evaluation should then use an out-of-time customer split and a threshold based on validated contact, incentive, and churn-loss costs.

## License

This project is available under the MIT License.
