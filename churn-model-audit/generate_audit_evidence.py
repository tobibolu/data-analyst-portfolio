"""Generate the recruiter facing audit table from the notebook metrics file."""

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent


def main() -> None:
    metrics = json.loads((PROJECT_DIR / "model_metrics.json").read_text())
    evidence = {
        "decision": metrics["status"],
        "source_rows": metrics["source_rows"],
        "unique_customers": metrics["unique_customers"],
        "training_customers": metrics["training_customers"],
        "holdout_customers": metrics["holdout_customers"],
        "withdrawn_earlier_auc": "above 0.92",
        "cv_auc_mean": metrics["cv"]["roc_auc"]["mean"],
        "cv_auc_std": metrics["cv"]["roc_auc"]["std"],
        "holdout_auc": metrics["holdout_default_0_50"]["roc_auc"],
        "holdout_average_precision": metrics["holdout_default_0_50"]["average_precision"],
        "selected_threshold": metrics["threshold_policy"]["selected_threshold"],
        "holdout_customers_flagged": (
            metrics["holdout_cost_selected"]["tp"] + metrics["holdout_cost_selected"]["fp"]
        ),
    }
    (PROJECT_DIR / "audit_evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown = f"""# Generated Audit Evidence

| Stage | ROC AUC | Decision |
|---|---:|---|
| Earlier portfolio claim | {evidence['withdrawn_earlier_auc']} | Withdrawn |
| Five fold cross validation | {evidence['cv_auc_mean']:.3f} ± {evidence['cv_auc_std']:.3f} | No reliable ranking signal |
| Untouched customer holdout | {evidence['holdout_auc']:.3f} | Do not deploy |

The cost selected threshold was {evidence['selected_threshold']:.2f} and flagged {evidence['holdout_customers_flagged']} of {evidence['holdout_customers']} holdout customers.
"""
    (PROJECT_DIR / "audit_evidence.md").write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()

