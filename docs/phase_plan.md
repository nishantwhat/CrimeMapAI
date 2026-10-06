# CrimeMapAI --- Phase-by-Phase Execution Plan

## Phase 0 --- Foundation

**Goal:** reproducible group-project infrastructure.

Outputs: - Git repository - environment - folder structure - README -
progress.md - requirements - configuration

Exit: any team member can clone and run the project.

## Phase 1 --- Data Understanding

**Goal:** determine what the raw data actually means.

Tasks: - profile all files; - build data dictionary; - determine row
grain; - inspect missingness; - inspect duplicate keys; - compare
geography; - compare years; - validate composite keys; - audit 2024
compatibility.

Exit statement:

> One row represents X, at geography Y, for period Z.

## Phase 2 --- Preprocessing

Tasks: - type normalization; - year normalization; - missing-value
strategy; - duplicate handling; - range validation; - geography
normalization; - population/exposure integration; - deterministic
transformation.

Output: model-ready dataset + quality report.

## Phase 3 --- EDA + Spatio-Temporal Analysis

Tasks: - yearly trends; - city comparisons; - crime composition; -
maps; - hotspots; - spatial autocorrelation where supported; - trend
changes.

Output: EDA notebook + findings.

## Phase 4 --- Feature Engineering

Candidate features:

``` text
lag_1
lag_2
rolling_mean_3
rolling_std_3
year_over_year_change
recent_trend
crime-category totals
crime ratios
historical risk
population-adjusted rates
```

Critical rule:

> Features for t+1 must use only information available through t.

## Phase 5 --- Modeling

Regression: - persistence baseline; - Ridge; - Random Forest; - Gradient
Boosting.

Classification: - Logistic Regression; - Random Forest; - Gradient
Boosting.

Compare simple and nonlinear models.

## Phase 6 --- Evaluation

Regression: - MAE - RMSE - R²

Classification: - Macro F1 - Weighted F1 - precision - recall -
confusion matrix - high-risk recall - PR-AUC where appropriate

Additional: - temporal stability; - error analysis; - hotspot detection
performance.

## Phase 7 --- Dashboard

Core screens:

1.  Overview
2.  Map
3.  City analysis
4.  Model insights
5.  Prediction / what-if

## Phase 8 --- Demo Notebook

User flow:

``` text
Select city
→ select crime category
→ select year
→ predict
→ display rate
→ display risk
→ display trend
→ display explanation
→ display caveats
```

## Phase 9 --- Finalization

-   report;
-   presentation;
-   viva;
-   reproducibility test;
-   final repository;
-   final progress update.
