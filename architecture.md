# CrimeMapAI --- Architecture

## Layered Design

``` text
NCRB / IDP / external sources
            ↓
      Raw ingestion
            ↓
    Schema + grain audit
            ↓
     Geography layer
            ↓
     Data validation
            ↓
       Preprocessing
            ↓
    Feature engineering
            ↓
   Temporal validation
            ↓
       Model layer
            ↓
 Evaluation + error analysis
            ↓
      ┌─────┴─────┐
      ↓           ↓
 Dashboard     Demo notebook
```

## Data Layer

`src/crimemapai/data/`

Responsibilities:

-   loading;
-   source adapters;
-   schema checks;
-   grain checks;
-   merge checks;
-   geography mapping.

## Feature Layer

`src/crimemapai/features/`

Responsibilities:

-   lag features;
-   rolling statistics;
-   trends;
-   crime aggregates;
-   rates;
-   spatial features.

Every feature must have a documented availability time.

## Model Layer

`src/crimemapai/models/`

Responsibilities:

-   baselines;
-   regression;
-   classification;
-   training;
-   prediction;
-   artifact persistence.

## Evaluation Layer

`src/crimemapai/evaluation/`

Responsibilities:

-   temporal splitting;
-   metrics;
-   model comparison;
-   error analysis.

## Dashboard

The dashboard consumes saved artifacts.

It must not retrain the model when opened.

``` text
processed data
+
preprocessor
+
model
↓
Streamlit
```

## Configuration

Keep target, geography, paths, validation years and model settings in
configuration rather than hardcoding them inside notebooks.

## Reproducibility

Each model artifact should record:

-   model type;
-   data version;
-   feature version;
-   target definition;
-   train/validation/test periods;
-   seed;
-   metrics;
-   environment/package information.
