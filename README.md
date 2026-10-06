# CrimeMapAI

**ML-Based Crime Risk Prediction and Spatio-Temporal Analysis of Indian
Metropolitan Cities**

Course: Applications and Use Cases of Machine Learning (TE7483)\
Assessment: ESE AUCML Case Study Project

## Objective

CrimeMapAI is an end-to-end ML case study for:

1.  understanding crime patterns across Indian metropolitan areas;
2.  analyzing spatial and temporal variation;
3.  predicting future crime rate/count;
4.  optionally classifying locations into Low/Medium/High risk;
5.  presenting results through an interactive dashboard and demo
    notebook.

The project is deliberately modular so ingestion, preprocessing,
features, models, evaluation and presentation can be replaced
independently.

## Critical Scope Decision

The currently inspected India Data Portal resources are primarily
**district-level**, while the project title says **metropolitan
cities**.

Therefore we must explicitly define:

``` text
NCRB district → geographic mapping → metropolitan/city unit
```

or use direct NCRB metropolitan-city tables where available.

A district must never be silently treated as a city.

## Current Dataset

The inspected India Data Portal cybercrime resource reports:

-   yearly frequency;
-   district granularity;
-   `state_code` and `district_code`;
-   36 states/UTs;
-   approximately 752 districts;
-   41 indicators;
-   coverage 2017--2022.

Important fields include `id`, `year`, state/district fields,
`registration_circles`, and crime indicators.

**Important:** `id` is not automatically a cross-dataset join key.
Uniqueness within each file does not prove semantic compatibility.

## 2024 Extension

NCRB Crime in India 2024 is now available. The project may extend the
historical series, but 2024 must not simply be appended to 2017--2022.

Required audit:

``` text
2017–2022 + 2023 + 2024
        ↓
schema audit
        ↓
geography audit
        ↓
indicator-definition audit
        ↓
classification/legal-change audit
        ↓
append only if compatible
```

## Repository

``` text
CrimeMapAI/
├── data/{raw,interim,processed,external}
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_eda_spatiotemporal.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_modeling.ipynb
│   ├── 06_evaluation.ipynb
│   └── 07_demo.ipynb
├── src/crimemapai/
├── configs/
├── dashboard/
├── artifacts/
├── reports/
├── tests/
├── docs/
├── progress.md
├── metrics.md
├── architecture.md
└── README.md
```

## Development Rules

-   Raw data is immutable.
-   Reusable logic belongs in `src/`, not notebooks.
-   Every dataset gets a source/version record.
-   Validate grain before merging.
-   Never create historical features from future information.
-   Use temporal validation.
-   Save fitted preprocessors and model artifacts.
-   Update `progress.md` after every major milestone.
-   Do not commit large raw datasets unless licensing and repository
    policy permit it.

## Setup

``` bash
git clone <REPOSITORY_URL>
cd CrimeMapAI

python -m venv .venv
.venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

jupyter lab
```

Dashboard:

``` bash
streamlit run dashboard/app.py
```

## Git

``` bash
git init
git branch -M main
git add .
git commit -m "chore: initialize CrimeMapAI project"
git remote add origin <REPOSITORY_URL>
git push -u origin main
```

Feature branches:

``` bash
git checkout -b feat/data-understanding
git add .
git commit -m "feat: add dataset understanding"
git push -u origin feat/data-understanding
```

Commit prefixes:

``` text
feat: fix: refactor: docs: test: data: model: dashboard: chore:
```

## Pipeline

``` text
Sources
  ↓
Raw ingestion
  ↓
Data understanding
  ↓
Schema + grain validation
  ↓
Geographic mapping
  ↓
Preprocessing
  ↓
EDA
  ↓
Feature engineering
  ↓
Temporal validation
  ↓
Baseline
  ↓
ML models
  ↓
Evaluation + error analysis
  ↓
Dashboard + demo
  ↓
Report + viva
```
