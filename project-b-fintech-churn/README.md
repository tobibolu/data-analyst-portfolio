# MTN Nigeria Customer Churn Analysis Pipeline

**Author:** Tobi Bolu
**GitHub:** [tobibolu](https://github.com/tobibolu)
**LinkedIn:** [linkedin.com/in/tobibolu](https://www.linkedin.com/in/tobibolu/)

---

## Project Overview

This project takes a real Nigerian telecom customer dataset and builds a full churn analysis pipeline: exploratory analysis, A/B test simulation for a retention campaign, a logistic regression churn model, and a Streamlit dashboard for monitoring at-risk customers.

### Dataset
- **Source:** [MTN Nigeria Customer Churn](https://www.kaggle.com/datasets/oluwademiladeadeniyi/mtn-nigeria-customer-churn)
- **Size:** 974 customer records, 17 features (expanded to 21 after feature engineering)
- **Key Variables:** Customer Churn Status (Yes/No), Customer Tenure, Satisfaction Rate, Subscription Plan, Data Usage, Total Revenue, MTN Device, Reasons for Churn

---

## Project Structure

```
project-b-fintech-churn/
├── 01_eda_cleaning.ipynb          # Data exploration & feature engineering
├── 02_ab_test_analysis.ipynb      # A/B test simulation for retention campaign
├── 03_churn_model.ipynb           # Predictive model & risk scoring
├── app.py                         # Streamlit dashboard
├── cleaned_data.csv               # (generated) Cleaned dataset
├── predictions.csv                # (generated) Risk scores & levels
└── README.md                      # This file
```

---

## Notebooks

### [01 EDA & Cleaning](https://nbviewer.org/github/tobibolu/data-analyst-portfolio/blob/main/project-b-fintech-churn/01_eda_cleaning.ipynb)

**Purpose:** Explore data quality, univariate/bivariate distributions, and engineer features.

**Key sections:**
- Adaptive column discovery (identifies churn, tenure, usage, etc. by pattern matching)
- Data quality assessment (missing values, duplicates, outliers)
- Statistical profiling (descriptive stats, distributions)
- Churn visualizations (overall rate, patterns by segment)
- Outlier detection (IQR method)
- Feature engineering (ordinal encoding, interactions, ratios, binning)
- **Output:** `cleaned_data.csv`

**Key insights:**
- 29.2% overall churn rate (284 out of 974 customers)
- Zero missing values except "Reasons for Churn" (missing for non-churners, as expected)
- Top churn reasons: relocation, better competitor offers, costly data plans, poor network
- Satisfaction ratings and customer reviews are strong churn signals
- Engineered 4 new features: tenure x usage interaction, revenue-per-usage ratio, age bins, subscription plan encoding

---

### [02 A/B Test Analysis](https://nbviewer.org/github/tobibolu/data-analyst-portfolio/blob/main/project-b-fintech-churn/02_ab_test_analysis.ipynb)

**Purpose:** Design and simulate an SMS re-engagement campaign targeting at-risk customers.

**Key sections:**
- At-risk customer identification (tenure, usage, complaints)
- Hypothesis framing (H0 vs H1 for retention lift)
- Sample size calculation (power analysis with Cohen's h)
- A/B test simulation (control/treatment assignment, binomial outcomes)
- Statistical tests (chi-squared, two-proportion z-test, 95% CI)
- Business impact estimation (revenue, ROI, cost per retained customer)

**Key findings:**
- 316 at-risk customers identified (32.4%) based on low tenure (<7.3 months) and low data usage (<47.6 GB)
- At-risk segment churn rate: 25.3% vs 29.2% overall
- Simulated 6% retention lift; observed 4.25pp absolute lift (treatment: 78.9% vs control: 74.7%)
- Chi-squared p=0.45, z-test p=0.19 — result not statistically significant (study was underpowered: needed 1,505 customers, had 316)
- Directionally positive: estimated 4,330% ROI at \$0.50/SMS, but requires properly powered follow-up

---

### [03 Churn Model](https://nbviewer.org/github/tobibolu/data-analyst-portfolio/blob/main/project-b-fintech-churn/03_churn_model.ipynb)

**Purpose:** Build logistic regression model to predict churn and score customer risk.

**Key sections:**
- Feature selection (correlation analysis, ID column removal)
- Feature preparation (categorical encoding, numerical scaling)
- Stratified train/test split (80/20, balanced classes)
- Logistic regression (balanced class weights)
- Model evaluation (confusion matrix, ROC/AUC, precision-recall)
- Threshold optimization (F1 score across thresholds)
- Feature importance (coefficient visualization)
- Risk scoring (Critical/High/Medium/Low assignments)
- **Output:** `predictions.csv`

**Key metrics:**
- ROC AUC: 0.9204 (excellent discrimination)
- Test accuracy: 93.3%, Precision: 97.8%, Recall: 78.9%
- Optimal threshold: 0.50, F1 score: 0.874
- 231 Critical-risk customers (23.7%), 17 High-risk (1.7%), 71 Medium (7.3%), 655 Low (67.2%)
- Top drivers: geographic location (state-level variation), churn reasons (costly plans, poor network), Adamawa state (+1.46 coefficient)

---

## Dashboard

Run the interactive dashboard with:

```bash
streamlit run app.py
```

**Features:**
- Real-time metrics (total customers, churn rate, avg risk probability, critical count)
- Risk distribution visualizations
- At-risk customer ranking & export
- Probability distribution histogram
- Feature importance chart
- Downloadable filtered results

---

## How to Run

### Prerequisites
```bash
pip install pandas numpy scikit-learn scipy plotly kagglehub streamlit
```

### Step 1: Data Cleaning & Exploration
```bash
jupyter notebook 01_eda_cleaning.ipynb
```
- Downloads MTN dataset from Kaggle
- Generates `cleaned_data.csv`

### Step 2: A/B Test Simulation
```bash
jupyter notebook 02_ab_test_analysis.ipynb
```
- Loads `cleaned_data.csv`
- Simulates SMS retention campaign
- Outputs statistical analysis & business impact

### Step 3: Build Churn Model
```bash
jupyter notebook 03_churn_model.ipynb
```
- Loads `cleaned_data.csv`
- Trains logistic regression
- Generates `predictions.csv` with risk scores

### Step 4: Launch Dashboard
```bash
streamlit run app.py
```
- Opens interactive dashboard in browser
- Filters, visualizations, & exports

---

## Tools & Libraries

- **Data:** pandas, numpy
- **Modeling:** scikit-learn, scipy
- **Visualization:** Plotly
- **Dashboard:** Streamlit
- **Data Source:** Kaggle Hub

---

## Key Findings

### Churn Drivers
- Geographic location is the strongest predictor, with Adamawa, Bayelsa, and Taraba states showing significantly higher churn
- Stated reasons: costly data plans, poor network quality, and poor customer service
- Weak individual correlations (<0.1) suggest churn is driven by feature combinations, not single variables

### At-Risk Segment
- 248 customers (25.5%) flagged as Critical or High risk
- Model identifies churners with 97.8% precision and 78.9% recall
- Top 10 at-risk customers all have >99.8% churn probability

### Retention Opportunity
- SMS re-engagement campaign showed 4.25pp retention lift (directionally positive but not statistically significant due to small sample)
- Estimated ROI of 4,330% at \$0.50/SMS, with \$22.57 cost per retained customer
- Recommendation: expand sample to 1,500+ customers for a properly powered follow-up test

---

## Author

**Tobi Bolu**
- LinkedIn: [linkedin.com/in/tobibolu](https://www.linkedin.com/in/tobibolu/)
- GitHub: [github.com/tobibolu](https://github.com/tobibolu)
- Portfolio: [data-analyst-portfolio](https://github.com/tobibolu/data-analyst-portfolio)

---

## License

This project is open source and available under the MIT License.
