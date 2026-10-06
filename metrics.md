# CrimeMapAI --- Evaluation Metrics

## Regression

### Primary

**MAE**

``` text
mean(|y - y_hat|)
```

Directly interpretable in target units.

**RMSE**

``` text
sqrt(mean((y - y_hat)^2))
```

Penalizes large misses more strongly.

### Secondary

**R²** --- explained variance relative to baseline.

Optional: - Median Absolute Error - RMSLE where non-negative/log-scale
error is appropriate - MAPE only with careful zero handling

## Classification

For Low/Medium/High risk:

-   Macro F1 --- primary
-   Weighted F1 --- complementary
-   Precision
-   Recall
-   Confusion matrix
-   High-risk recall
-   High-risk precision
-   PR-AUC when high-risk is rare
-   ROC-AUC as supplementary where appropriate

Accuracy is not the primary metric.

## Hotspot Analysis

If a top-k hotspot list is produced:

-   Top-k hit rate
-   hotspot precision
-   hotspot recall
-   hotspot F1
-   spatial overlap

## Spatial Statistics

**Moran's I** can quantify spatial autocorrelation.

It is an analytical/spatial statistic, not a substitute for predictive
model metrics.

## Baseline

At minimum compare against persistence:

``` text
prediction(t+1) = observed(t)
```

This is essential because a complex model is not useful if it cannot
beat a trivial temporal baseline.

## Validation

Do not rely only on random train/test splitting.

Preferred:

``` text
Train: earlier years
Validation: later year(s)
Test: latest compatible year
```

Use rolling-origin validation for model selection.

## Final Comparison

  Model                    MAE   RMSE    R²   Macro F1   High-Risk Recall
  ---------------------- ----- ------ ----- ---------- ------------------
  Persistence baseline                  N/A        N/A                N/A
  Ridge                                                
  Random Forest                                        
  Gradient Boosting                                    
  Final model                                          

Do not populate the table with invented values.

## Error Analysis

Required analysis:

-   worst errors;
-   systematic underprediction;
-   systematic overprediction;
-   error by city;
-   error by year;
-   error by crime category;
-   high-risk vs low-risk errors.

The final report must answer:

> Where does the model fail, and why?
