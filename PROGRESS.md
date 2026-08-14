# Fashion Trend Forecasting — Progress Log

## Project goal
Forecast demand for fashion subcategories (jean fits, jacket styles) using the 
H&M Personalized Fashion Recommendations dataset, then translate forecasts into 
inventory policy recommendations (safety stock, reorder points).

## Status: Phase 2 (in progress)

## Decisions made so far

**Data source**: H&M Kaggle dataset (articles.csv, customers.csv, transactions_train.csv).
Downloaded via Kaggle API, images excluded to save space.

**Category scope**: Originally planned skinny/baggy/bootcut jeans and denim/leather/canvas 
jackets. After checking real `detail_desc` text in the data, found "baggy," "bootcut," 
and "canvas" barely exist in H&M's actual product vocabulary (2, 12, and 14 matches out 
of thousands). Pivoted to categories based on real keyword frequency instead:

- **Trousers fit categories**: skinny_slim, tapered, straight, wide_relaxed, regular
  (built via keyword matching on `detail_desc`, saved to `data/interim/trousers_tagged.csv`, 
  8,494 tagged items)
- **Jacket style categories**: denim, leather_biker (merged leather + biker since they 
  overlap heavily), bomber (saved to `data/interim/jackets_tagged.csv`, 843 tagged items)

**Tech stack**: pandas for articles.csv (small), DuckDB for transactions_train.csv 
(3.2GB, 31.8M rows — too big to comfortably load in pandas).

## Completed
- [x] Phase 1: Project setup (venv, Kaggle API, folder structure)
- [x] Phase 1: Explored articles.csv, confirmed real keyword vocabulary
- [x] Phase 1: Built and validated tagging functions for trousers + jackets
- [x] Pushed to GitHub: https://github.com/cristianowen/fashion-trend-forecasting
  (data/ folder excluded via .gitignore — too large for GitHub)

## Completed (continued)
- [x] Phase 2: Joined tagged articles against transactions_train.csv using DuckDB 
  (inner join on article_id, grouped by date + category)
- [x] Phase 2: Built daily demand time series — trousers_ts (3670 rows, 5 fit 
  categories) and jackets_ts (2200 rows, 3 style categories)
- [x] Phase 2: Saved both to data/processed/trousers_daily_sales.csv and 
  jackets_daily_sales.csv

## Completed (continued)
- [x] Phase 3: Plotted daily trouser/jacket sales by subcategory
- [x] Phase 3: Applied 30-day rolling average to smooth daily noise and reveal trends
- [x] Phase 3: Validated trouser trend isn't purely a supply-side artifact — checked 
  distinct products sold per day alongside units sold

## Key findings (Phase 3)

**Trousers — genuine multi-year trend, not just seasonal noise:**
- skinny_slim declined ~55% in units sold over 2018-2020, while distinct products 
  sold declined only ~35% over the same period — the gap suggests real declining 
  demand per product, not just H&M stocking fewer styles
- tapered and straight both grew steadily over the same window (roughly doubled)
- wide_relaxed and regular stayed small and flat throughout

**Jackets — seasonal cycle, not a directional trend:**
- denim and leather_biker both show a strong annual cycle: rising Jan-Feb, peaking 
  Mar-Apr, declining through summer to a low around Aug-Sep — consistent with 
  jackets being a seasonal category
- denim consistently outsells leather_biker at every peak
- bomber stays small and flat, minor category

**Implication for Phase 4 (forecasting)**: trousers and jackets likely need different 
modeling approaches — trousers has a real underlying trend to capture, jackets is 
dominated by seasonality rather than trend.

## Completed (continued)
- [x] Phase 4: Built naive baseline (MAE 531.0) and 7-day moving average baseline 
  (MAE 595.6 — worse than naive, since moving average lags behind a real sustained 
  trend) for skinny_slim trousers
- [x] Phase 4: Built linear regression trend model for skinny_slim — beat naive 
  baseline (MAE 460.2, ~13% improvement). Confirmed slope (-2.58 units/day decline) 
  and intercept by deriving the least-squares formula manually and matching sklearn's 
  output exactly.
- [x] Phase 4: Used 80/20 chronological train/test split (train: Sep 2018–Apr 2020, 
  test: Apr–Sep 2020). Note: test period overlaps COVID-19 disruption — worth 
  revisiting if results look off.

## Completed (continued)
- [x] Phase 4: Built naive baseline and linear regression trend model, evaluated 
  across all 5 trouser fit categories
- [x] Phase 4: CAUGHT AND FIXED a methodology bug — initial skinny_slim comparison 
  (naive 531.0 vs linear 460.2) was invalid because naive was measured across the 
  full dataset while linear was measured only on the test set. Rebuilt evaluation 
  so both models are scored on the identical held-out test period (last 20% of days, 
  chronological split).

## Corrected Phase 4 results (naive vs linear regression, same test period)

| Category      | MAE Naive | MAE Linear | Slope   | Naive wins? |
|---------------|-----------|------------|---------|-------------|
| tapered       | 249.0     | 323.4      | +0.525  | Yes         |
| straight      | 164.9     | 259.9      | -0.030  | Yes         |
| skinny_slim   | 280.5     | 460.2      | -2.583  | Yes         |
| wide_relaxed  | 44.7      | 87.2       | -0.322  | Yes         |
| regular       | 16.7      | 133.6      | +0.285  | Yes         |

**Finding**: Naive baseline beats linear regression on every trouser category once 
evaluated fairly. Likely causes: (1) test period overlaps COVID-19 disruption, which 
may have broken the "normal" linear trend the model learned from training data; 
(2) a straight line can't adapt to trends that slow down, speed up, or reverse — 
real fashion trends aren't perfectly linear.

## Completed (continued)
- [x] Phase 4: Ruled out COVID as the cause of linear regression underperformance — 
  tested on a pre-COVID holdout (Nov 2019–Jan 2020), naive STILL beat linear on 4/5 
  categories. Real cause is more fundamental: straight-line models can't capture 
  short-term spikes (holidays/sales) in the data.
- [x] Phase 4: Built engineered features (day_of_week, month, day_of_year, lag_1, 
  lag_7, rolling_7) and trained a gradient boosting model (sklearn's 
  HistGradientBoostingRegressor — used instead of XGBoost/LightGBM, which need libomp 
  not installed on this machine; same gradient-boosted-trees concept).
- [x] Phase 4: Gradient boosting STILL did not beat naive on skinny_slim daily 
  (naive 282.4 vs GB 363.8).

## Key finding (Phase 4)
For NOISY DAILY retail data, the naive baseline is remarkably hard to beat — a common, 
well-documented real-world result. Daily sales are dominated by short-term persistence 
(tomorrow ≈ today), which is exactly what naive captures. More complex models dilute 
this strong single signal and can overfit to noise. This is a legitimate finding, not 
a failure — it demonstrates rigorous baseline comparison and honest evaluation.

## Completed (continued)
- [x] Phase 4: Reframed forecasting to WEEKLY granularity (daily too noisy). Naive 
  still narrowly beat linear/gradient boosting at 1-week-ahead — because naive always 
  has last week's real value, an unfair advantage for such a short horizon.
- [x] Phase 4: Installed Prophet (worked cleanly, unlike XGBoost/LightGBM). Fit on 
  denim jacket weekly sales with yearly seasonality enabled.
- [x] Phase 4: Prophet successfully captured the seasonal cycle that ALL earlier 
  models missed — confirmed via component decomposition (trend + yearly seasonality 
  plotted separately).
- [x] Phase 4: KEY INSIGHT — recognized the 1-week-ahead naive comparison was unfair 
  (naive gets constant fresh data; misaligned with real inventory need). Reran at a 
  realistic 4-week-ahead horizon (typical supplier lead time).

## HEADLINE RESULT (Phase 4)
On the realistic 4-week-ahead forecasting task (what inventory planning actually 
requires), PROPHET BEATS NAIVE BY ~42%:
- Naive (4-week lag) MAE: 308.5
- Prophet MAE: 178.8
- Avg weekly denim jacket sales: 793

Interpretation: naive only wins at very short horizons where it gets constant real-data 
updates. For any realistic planning horizon, a seasonality-aware model (Prophet) is 
dramatically better. This is the result that justifies the whole modeling effort.

## Prophet component findings (denim jackets)
- Trend: steady multi-year decline (~1030 → ~600 units)
- Yearly seasonality: strong spring peak (~+930 above baseline, late March/April), 
  deep late-fall trough (~-600, November) — a ~1500-unit swing purely from time of year
- Directly actionable for inventory: stock up for spring, wind down into late fall

## Next steps
- [ ] Run Prophet on remaining jacket styles (leather_biker, bomber) and trouser fits
- [ ] Phase 5: Translate forecasts into inventory policy (safety stock, reorder points)
- [ ] Phase 6: Dashboard + final writeup

## Files
- `notebooks/04_forecasting.ipynb` — Phase 4 (in progress, skinny_slim model built)

## Files
- `notebooks/01_explore_articles.ipynb` — Phase 1 (tagging)
- `notebooks/02_build_timeseries.ipynb` — Phase 2 (in progress)
- `data/interim/trousers_tagged.csv`, `data/interim/jackets_tagged.csv` — tagged data 
  (not on GitHub, regenerate by rerunning notebook 01)