# CrimeMapAI — Progress & Handoff Context

> **Authoritative project handoff.** This file records the project's intent, data decisions, verified findings, implementation state, unresolved issues, and the exact next action. A new contributor or LLM should be able to continue the project from this file without relying on conversational context.

---

## 1. Project Identity

**Project:** CrimeMapAI  
**Working title:** ML-Based Crime Risk Prediction and Spatio-Temporal Analysis of Indian Metropolitan Cities  
**Course:** Applications and Use Cases of Machine Learning  
**Course code:** TE7483  
**Assessment:** Group ESE Case Study Project  
**Primary operational dataset:** India Data Portal / NCRB district-wise cyber-crime data, 2017–2022  

### Scope clarification
The supplied primary dataset is **district/registration-circle level**, not a clean metropolitan-city table. The implementation therefore currently operates at **district-year grain**. The final report must either:

1. explicitly redefine the operational scope as district-level Indian cybercrime analysis, or
2. introduce a defensible district→metropolitan-area mapping before claiming metropolitan-city predictions.

Do **not** silently describe a district as a metropolitan city.

---

## 2. Project Intent

The project must demonstrate a complete, defensible ML case study rather than merely train a model:

```text
raw government data
    ↓
data understanding
    ↓
data-quality + grain validation
    ↓
preprocessing
    ↓
EDA / spatio-temporal analysis
    ↓
feature engineering
    ↓
baseline + ML models
    ↓
temporal evaluation
    ↓
error analysis + interpretation
    ↓
dashboard / demo
    ↓
final report + viva
```

### Primary ML question

> Given information available for a district through year `t`, can we predict the district's **reported cyber-crime count in year `t+1`**?

This is a **next-year reported-count prediction** task. It is not currently a population-normalised crime-rate prediction because no defensible population denominator is present in the supplied primary dataset.

### Responsible-use framing

The project predicts patterns in **reported/registered cybercrime**, not the probability that a person will commit a crime. Model outputs should be framed for analytical/resource-planning use and not as evidence for punitive decisions about individuals.

---

## 3. ESE Rubric Requirements

| Component | Marks |
|---|---:|
| Problem refinement / use-case relevance | 3 |
| Dataset understanding / preprocessing / features | 4 |
| ML methodology / pipeline | 5 |
| Implementation / project execution | 5 |
| Results / metrics / comparative analysis | 5 |
| Final report / documentation | 3 |
| Communication | 2 |
| Viva / project defense | 3 |
| **Total** | **30** |

The rubric expects:
- source and dataset description;
- dimensions and attributes;
- target definition;
- data types and missing values;
- preprocessing and feature engineering;
- complete ML pipeline;
- validation methodology;
- suitable metrics;
- comparative analysis;
- reproducible implementation;
- report, conclusion, future scope and references;
- ability to defend dataset/model/methodology/results/limitations in viva.

---

# 4. Repository / Notebook Convention

The notebooks are intentionally simple and use project-relative paths. Do **not** add `PROJECT_ROOT`, `sys.path`, or `/mnt/data` fallback machinery to normal notebook cells.

When notebooks are run from the `notebooks/` directory, canonical paths are:

```text
../data/raw/
../data/processed/
```

### Canonical raw files

```text
data/raw/
├── districtwise-cyber-crimes-2017-onwards.csv
└── districtwise-cyber-crimes-2024-onwards.csv
```

### Processed artifacts

```text
data/processed/
├── district_year_panel.csv
├── model_table.csv
└── model_table_v2.csv
```

### Notebook sequence

```text
01_data_understanding.ipynb
01_1_dataset_compatibility.ipynb
02_data_preprocessing.ipynb
03_eda_spatiotemporal.ipynb
04_feature_engineering.ipynb
05_modeling.ipynb          ← next major notebook
06_evaluation.ipynb
07_demo.ipynb
```

---

# 5. Dataset Inventory

## 5.1 2017–2022 dataset

File:

```text
data/raw/districtwise-cyber-crimes-2017-onwards.csv
```

Verified raw properties:

- **5,322 rows**
- **48 columns**
- years **2017–2022**
- no missing values in the raw dataset
- no negative values in the numeric crime-count fields
- source contains state, district, registration-circle and crime-category information

## 5.2 2024 dataset

File:

```text
data/raw/districtwise-cyber-crimes-2024-onwards.csv
```

Verified earlier:

- **964 rows**
- **56 columns**
- year = 2024
- 2024 contains IPC/BNS-era field changes and additional indicators

The 2024 file is **not part of primary model training**.

---

# 6. Frozen 2024 Decision

### Decision

> **Primary modelling uses the 2017–2022 dataset only.** The 2024 dataset is excluded from primary training and target construction because its IPC/BNS-era indicator definitions are not source-verified as directly equivalent to the historical indicators.

The project therefore does **not** perform a blind:

```text
2017–2022 + 2024 → append
```

The 2024 data may later be used for contextual discussion or a separately designed validation/extension study if a defensible legal/indicator crosswalk is established.

### Why this is the chosen strategy

Forcing non-equivalent legal/classification fields into a longitudinal panel would create an artificial distribution change and could invalidate the target/feature interpretation. Restricting the primary experiment to the internally consistent 2017–2022 source is methodologically safer.

### 2023 gap

The supplied primary dataset ends at 2022 and the supplied 2024 dataset starts at 2024. **2023 is absent.**

Therefore:

- 2022 cannot be used as a next-year prediction origin in the current primary dataset;
- no synthetic/interpolated 2023 target is created;
- the supervised prediction origins are 2017–2021.

---

# 7. 01 — Data Understanding

Notebook:

```text
notebooks/01_data_understanding.ipynb
```

Purpose:
- independently load the supplied datasets;
- inspect schema;
- profile numeric/categorical/temporal fields;
- inspect missingness, duplicates, outliers and distributions;
- compare the two source files without blindly merging them.

### Path convention

Both raw files are loaded from:

```python
RAW_DIR = Path("../data/raw")
```

The notebook exposes the datasets through stable variables such as:

```python
df_2017_2022
df_2024
```

and retains the reusable dataset mapping where required by the existing profiling cells.

### Important profiler caveat

The earlier generic temporal profiler interpreted integer `year` values as nanosecond timestamps. This is a **profiler heuristic artifact**, not evidence that the year field is a timestamp. `year` must remain an integer 2017–2022.

---

# 8. 01_1 — Dataset Compatibility Audit

Notebook:

```text
notebooks/01_1_dataset_compatibility.ipynb
```

Reusable implementation:

```text
src/crimemapai/data/compatibility.py
```

Tests:

```text
tests/test_compatibility.py
```

The audit distinguishes:

```text
structural compatibility
```

from:

```text
semantic compatibility
```

A common column or unique key is not automatically a valid longitudinal join.

### Important conclusion

`id` is **not** a longitudinal key.

The correct operation between historical and 2024 files, if ever approved, would be a temporal append after harmonisation rather than a relational join on `id`.

---

# 9. Raw Grain — Critical Finding

The 2017–2022 raw file is **not one district row per year**.

Multiple registration-circle rows can occur inside a district-year.

Observed audit:

```text
Raw rows:                         5,322
Unique district-year keys:       4,347
Rows in repeated district-years:   975
Mean registration-circle rows:    1.224
Median registration-circle rows: 1
Maximum:                           10
```

Therefore the modelling grain is explicitly constructed as:

```text
state × district × year
```

by aggregating numeric crime counts across registration circles.

The raw `id` field is treated as an ingestion/row identifier and is excluded from modelling.

---

# 10. Critical Data-Quality Finding — District Labels

During preprocessing, the following audit produced:

```text
District-year groups with >1 state label:     12
District-year groups with >1 district label:   6
```

This is not a harmless formatting issue and must remain visible in the handoff.

The conflicts are concentrated in reused code combinations, including examples where:

- `state_code = 3`, `district_code = 608` contains `Punjab` rows with `S.A.S Nagar` and `Sas Nagar` label variants;
- `state_code = 24`, `district_code = 438` contains `Gujarat / Ahmadabad` rows and `Nagaland / Ahmadabad Western Railway` rows;
- `state_code = 24`, `district_code = 461` contains `Gujarat / Vadodara` rows and `Nagaland / Vadodara Western Railway` rows.

The current aggregation uses the first label for district metadata, which is **not yet an acceptable final data-quality policy** for the report.

### Required before final modelling

The next data-quality pass must explicitly decide whether these conflicting source records should be:

1. resolved using source documentation;
2. corrected only where the source provides a defensible mapping;
3. excluded from district-level modelling if their geographic identity cannot be established.

**Do not silently overwrite these labels.**

This is the main unresolved data-quality gate before the final model pipeline is frozen.

---

# 11. 02 — Data Preprocessing

Notebook:

```text
notebooks/02_data_preprocessing.ipynb
```

### Processing logic

```text
raw registration-circle rows
        ↓
validate schema / types / missingness / negatives
        ↓
aggregate crime counts
        ↓
district-year panel
        ↓
calendar-safe temporal features
        ↓
exact next-calendar-year target
        ↓
model table
```

### Target

Source-defined target:

```text
total_offences_under_ip
```

Prediction target:

```text
target_next_year = total_offences_under_ip(t+1)
```

No invented sum across crime categories is used as the primary target.

### Calendar-safe temporal construction

Do **not** use positional `groupby().shift()` as the final implementation because districts can have missing years.

The current implementation uses explicit year-keyed self-merges:

```text
t → t-1

t → t-2

t → t+1
```

A missing 2019 observation therefore does not cause 2020 to receive 2018 as its lag-1.

### Verified preprocessing output

```text
District-year panel: 4,347 rows × 46 columns
Model rows:           3,594
Prediction origins:   2017, 2018, 2019, 2020, 2021
```

Rows by origin year:

```text
2017    706
2018    707
2019    721
2020    730
2021    730
```

The 753 rows not used for next-year supervised learning correspond to district-years without an observed next calendar year, primarily 2022 plus other district-specific gaps.

### Missingness interpretation

The first execution showed approximately **40.65%** missingness for many lag-2 features. This is expected for structural historical gaps and the beginning of district histories; it must not be imputed as zero.

`target_yoy_growth` has much higher missingness because growth is undefined when the prior-year target is zero or unavailable. This is a mathematical/domain issue, not ordinary missing-data corruption.

---

# 12. 03 — EDA / Spatio-Temporal Analysis

Notebook:

```text
notebooks/03_eda_spatiotemporal.ipynb
```

Verified panel:

```text
Panel:    4,347 district-years
Years:    2017–2022
Districts: 753 observed district identities after aggregation
```

### Year-level reported offences

| Year | Reported offences | Mean | Median | District-years |
|---:|---:|---:|---:|---:|
| 2017 | 7,976 | 11.30 | 0 | 706 |
| 2018 | 8,647 | 12.23 | 0 | 707 |
| 2019 | 13,730 | 19.04 | 0 | 721 |
| 2020 | 20,201 | 27.67 | 1 | 730 |
| 2021 | 25,384 | 34.73 | 1 | 731 |
| 2022 | 33,786 | 44.93 | 1 | 752 |

Reported counts increase substantially over the period. This is a descriptive trend only; it must not automatically be interpreted as an equivalent increase in underlying incidence because reporting, registration, population and administrative coverage can also change.

### District concentration

Verified concentration of total reported offences:

```text
Top 5 districts:   50.90%
Top 10 districts:  58.37%
Top 20 districts:  65.93%
Top 50 districts:  76.04%
```

This is a major modelling characteristic. High-volume urban/district hubs are genuine observations and should **not** be deleted simply because generic IQR rules label them as outliers.

### 2022 top states

The supplied EDA output shows:

```text
Telangana        14,933
Maharashtra       7,482
Andhra Pradesh    1,922
Bihar             1,554
Odisha            1,219
Uttar Pradesh     1,165
Rajasthan           975
Gujarat             963
Tamil Nadu          593
Punjab              425
```

These are **reported counts**, not population-normalised risk rates.

### 2022 top districts

The largest reported counts include:

```text
Ranga Reddy, Telangana        5,395
Mumbai, Maharashtra           4,716
Hyderabad, Telangana          4,151
Yadadri Bhuvanagiri, Telangana 2,180
Gautam Buddha Nagar, UP         755
Warangal, Telangana             630
Visakhapatnam, Andhra Pradesh   583
Thane, Maharashtra              500
Pune, Maharashtra               448
Patna, Bihar                     362
```

### Target distribution

For `total_offences_under_ip`:

```text
Zero share:  51.55%
Mean:        25.24
Median:       0
Maximum:   5,395
Skewness:    20.12
```

The target is therefore strongly zero-inflated and right-skewed.

### Selected indicator sparsity

Examples from the EDA:

```text
identity_theft                    69.22% zeros
online_banking_fraud              82.36% zeros
otp_frauds                         90.11% zeros
other_frauds                       87.37% zeros
credit_card_debit_card_fraud       89.74% zeros
```

Zeros are treated as genuine count observations, not missing values.

### Modelling implication

The modelling stage must compare:

1. raw-count regression;
2. `log1p(target)` regression transformed back to count scale.

RMSE is expected to be strongly influenced by high-volume districts, so MAE and R² must also be reported and error analysis must explicitly inspect large-count districts.

---

# 13. 04 — Feature Engineering

Notebook:

```text
notebooks/04_feature_engineering.ipynb
```

Output:

```text
data/processed/model_table_v2.csv
```

Verified output:

```text
Final modelling rows: 3,594
Prediction-origin years: 2017–2021
Feature count: 230
Export shape: 3,594 × 235
```

### Features currently implemented

- calendar-safe lag-1 values;
- calendar-safe lag-2 values;
- two-year historical mean;
- two-year historical standard deviation;
- target historical lag aliases;
- target YoY change;
- target YoY growth;
- current-year `log1p` target history;
- crime-category total;
- non-zero category count;
- crime-category diversity;
- next-year target;
- `log1p(next-year target)`.

### Feature leakage policy

Future target fields are excluded from predictors:

```text
target_next_year
target_log1p
next_year
```

Current-year information is allowed because the prediction question is:

```text
information available at t → predict t+1
```

Registration-circle identifiers are not used as modelling features.

### Feature-missingness result

The most prominent missingness values include:

```text
target_offences_yoy_growth       ~73.82%
lag-2 crime variables             ~40.65%
```

These require deliberate modelling treatment. Do not replace structural lag gaps with zero.

### Target distribution in supervised table

```text
count:    3,594
mean:       28.23
median:      1.00
75th pct:   14.00
max:      5,395
zero share: ~49.86%
```

### Implementation issue fixed

An earlier `04_feature_engineering.ipynb` version defined `crime_cols` while excluding `total_offences_under_ip`, then attempted to reference:

```text
total_offences_under_ip_lag1
total_offences_under_ip_lag2
```

This caused the reported `KeyError`.

The notebook is now corrected so the target is included in the calendar-safe lag construction and then given readable aliases:

```python
df["total_offences_lag1"] = df["total_offences_under_ip_lag1"]
df["total_offences_lag2"] = df["total_offences_under_ip_lag2"]
```

The corrected notebooks were executed successfully in a clean notebook execution test.

A pandas `PerformanceWarning` about DataFrame fragmentation remains during repeated feature insertion. It is a performance warning, not a correctness failure. It can be optimized later without changing the feature definitions.

---

# 14. Current Files / Artifacts

### Notebooks

```text
notebooks/01_data_understanding.ipynb
notebooks/01_1_dataset_compatibility.ipynb
notebooks/02_data_preprocessing.ipynb
notebooks/03_eda_spatiotemporal.ipynb
notebooks/04_feature_engineering.ipynb
```

### Source modules

```text
src/crimemapai/data/loader.py
src/crimemapai/data/profile.py
src/crimemapai/data/grain.py
src/crimemapai/data/merge_audit.py
src/crimemapai/data/report.py
src/crimemapai/data/compatibility.py
src/crimemapai/data/cli.py
```

### Tests

```text
tests/test_grain.py
tests/test_profile.py
tests/test_compatibility.py
```

Previously verified project test state:

```text
8 passed
```

---

# 15. Data / Modelling Decisions That Must Not Be Reversed Casually

1. **Do not merge 2024 into the primary historical panel without a source-backed harmonisation decision.**
2. **Do not use `id` as a cross-dataset key.**
3. **Do not treat raw registration-circle rows as independent district observations.**
4. **Do not use positional lagging that bridges missing calendar years.**
5. **Do not fabricate a 2023 target.**
6. **Do not call `total_offences_under_ip` a population-normalised rate.**
7. **Do not delete high-count districts merely because generic IQR rules call them outliers.**
8. **Do not treat zeros in crime-count variables as missing values.**
9. **Do not use future target information in predictors.**
10. **Do not silently resolve conflicting source geography labels.**
11. **Do not use random train/test splitting as the primary validation strategy.**
12. **Do not derive risk labels using information from the validation/test period.**

---

# 16. Current Project State

```text
Phase 0 — Foundation                 COMPLETE
Phase 1 — Data understanding        COMPLETE / frozen for primary dataset
Phase 2 — Preprocessing             COMPLETE with one data-quality gate
Phase 3 — EDA                       COMPLETE
Phase 4 — Feature engineering       IMPLEMENTED / validated, final data-quality gate open
Phase 5 — Modelling                 NOT STARTED
Phase 6 — Evaluation                NOT STARTED
Phase 7 — Dashboard                 NOT STARTED
Phase 8 — Demo notebook             NOT STARTED
Phase 9 — Report / viva             IN PROGRESS as documentation groundwork
```

### Current gate

**Do not build the final model yet until the conflicting geography-label records are explicitly handled.**

The rest of the feature pipeline has been validated, but the source anomaly means the district identity definition is not yet completely frozen.

---

# 17. Immediate Next Action

## Step 1 — Resolve geography anomalies

Create a small data-quality audit table containing every `(state_code, district_code, year)` group with conflicting `state_name` or `district_name` values.

The audit should show:

```text
state_code
district_code
year
state_name values
district_name values
registration_circles
row count
crime-count total
recommended action
reason / source evidence
```

Do not automatically fix them by string normalization alone.

## Step 2 — Freeze the geography policy

After the anomaly decision, regenerate:

```text
data/processed/district_year_panel.csv
data/processed/model_table.csv
data/processed/model_table_v2.csv
```

and record the exact exclusion/correction rule in this file.

## Step 3 — Build `05_modeling.ipynb`

Only after the geography gate is closed:

```text
Persistence baseline
        ↓
Ridge
        ↓
Random Forest
        ↓
Gradient Boosting
        ↓
raw-count vs log1p target comparison
        ↓
rolling-origin temporal validation
```

### Recommended temporal evaluation

Because the usable next-year origins are 2017–2021, use time-ordered evaluation rather than random splitting.

Candidate rolling-origin structure:

```text
Train: 2017–2018 → Validate: 2019
Train: 2017–2019 → Validate: 2020
Train: 2017–2020 → Validate: 2021
```

A final untouched test period should be chosen carefully given the short six-year source history and the missing 2023 year. Do not claim a conventional 2022→2023 test unless 2023 data is obtained.

### Regression metrics

Headline:

```text
MAE
RMSE
R²
```

Secondary where useful:

```text
Median Absolute Error
RMSLE / log-scale diagnostics
```

Always evaluate transformed models on the original count scale as well.

### Baseline

Persistence:

```text
prediction(t+1) = observed count(t)
```

Every ML model must beat or at least be compared against this baseline.

---

# 18. Future Classification Layer

A Low/Medium/High risk classification layer is optional and must come **after** the regression target is validated.

If implemented:

- define labels from future target values;
- calculate thresholds using training data only inside each temporal fold;
- never calculate global thresholds using validation/test years;
- report Macro F1, class-wise precision/recall, high-risk recall, confusion matrix;
- do not make accuracy the headline metric if classes are imbalanced.

---

# 19. Dashboard / Demo Target

Planned user-facing flow:

```text
Select district
Select prediction year
        ↓
Historical trend
        ↓
Predicted next-year reported offences
        ↓
Risk category (if classification is validated)
        ↓
Expected change
        ↓
Feature/contributor explanation
        ↓
Methodology + responsible-use disclaimer
```

The dashboard must not imply individual criminal propensity.

---

# 20. Final Report Structure

Required sections:

1. Problem statement and motivation
2. Dataset/source and data dictionary
3. Data-grain discovery and data-quality decisions
4. Preprocessing
5. EDA and spatio-temporal findings
6. Feature engineering
7. ML methodology and model selection
8. Temporal validation strategy
9. Results and comparative analysis
10. Error analysis
11. Interpretation / explainability
12. Limitations
13. Responsible-use considerations
14. Conclusion
15. Future scope
16. References

The report must explicitly document:

- why 2024 was excluded;
- why the model operates at district-year grain;
- how registration-circle rows were aggregated;
- the 2023 gap;
- the geography anomaly and its resolution;
- why raw counts rather than rates are currently used;
- why temporal validation is used instead of random splitting.

---

# 21. Definition of Done

- [x] Source identified
- [x] Raw files supplied
- [x] 2017–2022 primary dataset frozen
- [x] 2024 exclusion decision documented
- [x] Raw schema profiled
- [x] Raw grain discovered
- [x] Registration-circle → district-year aggregation implemented
- [x] Next-year target defined
- [x] Calendar-safe temporal features implemented
- [x] EDA completed
- [x] Feature engineering implemented
- [ ] Conflicting geography labels resolved/documented
- [ ] Final modelling dataset frozen
- [ ] Persistence baseline established
- [ ] Multiple regression models compared
- [ ] Temporal validation completed
- [ ] Error analysis completed
- [ ] Optional classification layer validated
- [ ] Dashboard implemented
- [ ] Demo notebook implemented
- [ ] Final report completed
- [ ] Slides completed
- [ ] Viva preparation completed
- [ ] Reproducibility test completed

---

# 22. Session Handoff Template

After each major change, append a dated entry using:

```text
### YYYY-MM-DD — <phase/task>

Status:
What changed:
Why:
Files changed:
Tests/results:
Decisions:
Unresolved:
Next action:
```

---

# 23. Latest Session — 2026-10-07

### Status
Phase 4 feature engineering is implemented and executable. A KeyError in the previous implementation was diagnosed and fixed. The project is **not yet cleared for modelling** because the raw dataset contains a small but material geography-label inconsistency that must be explicitly handled.

### KeyError diagnosis
The previous `04_feature_engineering.ipynb` version excluded `total_offences_under_ip` from `crime_cols`, then attempted to access:

```text
total_offences_under_ip_lag1
total_offences_under_ip_lag2
```

Those columns could not exist under that construction, causing the observed KeyError. The corrected implementation includes the source target in calendar-safe lag generation and then creates readable aliases.

### Corrected execution
The corrected notebooks were executed successfully:

```text
02_data_preprocessing.ipynb   — executed successfully
03_eda_spatiotemporal.ipynb   — executed successfully
04_feature_engineering.ipynb  — executed successfully
```

Verified Phase 4 result:

```text
3,594 modelling rows
230 feature columns
235 exported columns including metadata/target fields
~49.86% zero next-year targets
```

### Additional data-quality discovery
The preprocessing audit found:

```text
12 district-year groups with >1 state label
6 district-year groups with >1 district label
```

These are concentrated around a small set of reused codes and include apparent source inconsistencies involving Gujarat/Nagaland and district-name spelling variants. They must be investigated before final model training.

### Files updated this session

```text
notebooks/01_data_understanding.ipynb
notebooks/01_1_dataset_compatibility.ipynb
notebooks/02_data_preprocessing.ipynb
notebooks/03_eda_spatiotemporal.ipynb
notebooks/04_feature_engineering.ipynb
progress.md
```

All notebook data paths now use the project-relative convention:

```text
../data/raw/
../data/processed/
```

### Next action
Resolve and document the conflicting geography-label records, regenerate the final modelling artifacts, then begin `05_modeling.ipynb` with a persistence baseline and rolling-origin temporal validation.
