# Churn Model Audit: Leakage Detection and Honest Validation

| Audit stage | ROC AUC | What the number means |
|---|---:|---|
| Earlier portfolio claim | Above 0.92 | Withdrawn after the audit found two leakage paths |
| Five fold cross validation | 0.488 ± 0.062 | No reliable ranking signal in the training customers |
| Untouched customer holdout | 0.465 | The corrected model is not suitable for deployment |

This repository now leads with one analysis project: an audit of whether a Nigerian telecom dataset can support prospective churn prediction.

The earlier model looked strong. The audit found that the score depended on information a real prediction system would not have:

1. `Reasons for Churn` describes the outcome after a customer has already left.
2. The 974 source rows represent 496 customers, so a row split placed records from the same person in both train and test data.

After removing post outcome and uncertain timing fields, aggregating to one row per customer, putting preprocessing inside the training pipeline, and evaluating once on an untouched 124 customer holdout, the score fell below random ranking. The correct decision was to stop deployment and specify the timestamped behavioural data a useful model would need.

## Why this is the headline project

A model audit is a better demonstration of senior analytical judgment than keeping an impressive number that cannot survive validation. The result shows three things a production decision needs:

- whether every feature exists at prediction time;
- whether the split matches the unit that will receive a prediction;
- whether the output can prioritise action on unseen customers.

[Open the full audit, executed notebook, evidence dashboard, and machine readable metrics.](./churn-model-audit/)

## Verified evidence

| Measure | Result |
|---|---:|
| Source rows | 974 |
| Unique customers | 496 |
| Training customers | 372 |
| Untouched holdout customers | 124 |
| Customer churn prevalence | 29.4% |
| Mean CV average precision | 0.323 ± 0.048 |
| Holdout average precision | 0.270 |
| Cost selected threshold | 0.11, selected from training predictions only |
| Holdout customers flagged | 124 of 124 |
| Deployment decision | Reject the model and collect better timed features |

The 5 to 1 false negative to false positive cost is an illustrative scenario, not an MTN financial estimate. Its chosen threshold flags everybody, which is further evidence that the current feature set cannot rank intervention priority.

## Supporting analysis archive

Earlier SQL ecommerce and cohort retention work remains under `supporting-analysis/` for reference. It is no longer presented as a three project portfolio and is not the lead resume evidence.

## Tools

Python, Pandas, scikit learn, stratified cross validation, leakage safe preprocessing, cost sensitive threshold analysis, Jupyter, Plotly, and Streamlit.

## Author

**Tobi Bolu** | [LinkedIn](https://www.linkedin.com/in/tobibolu/) | [GitHub](https://github.com/tobibolu)
