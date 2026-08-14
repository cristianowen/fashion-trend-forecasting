# Fashion Trend Forecasting — Progress Log

## Project goal
Forecast demand for fashion subcategories (jean fits, jacket styles) using the H&M 
Personalized Fashion Recommendations dataset (Kaggle), then translate forecasts into 
inventory policy recommendations (safety stock, reorder points). Portfolio project for 
a Data Science UCSD transfer application. Owner background: ran a clothing brand 
(accounting, supplier relations) + e-commerce internship.

## Status: Phase 4 COMPLETE. Starting Phase 5 (inventory policy).

## Environment / setup notes
- venv Python at: /Users/owenchen/Projects/H&M-trend-forecasting/fashion-trend-forecasting/venv/bin/python
- To reactivate: `cd fashion-trend-forecasting` then `source venv/bin/activate`
- Kernel: venv (3.14.6). If a notebook errors with NameError on a variable, the kernel 
  restarted — use "Run All" to reload variables top-to-bottom.
- XGBoost/LightGBM DO NOT WORK on this machine (need libomp; no Homebrew installed). 
  Used sklearn HistGradientBoostingRegressor instead. Prophet installed and works fine.
- Repo: https://github.com/cristianowen/fashion-trend-forecasting
- data/ folder is gitignored (too big for GitHub) — regenerate by rerunning notebooks.

## Data
- articles.csv (~105k products), customers.csv, transactions_train.csv (31.8M rows, 
  3.2GB, dates 2018-09-20 to 2020-09-22). In data/raw/. Images not downloaded.
- DuckDB used for joining the huge transactions file (too big for pandas in memory).

## Categories (built from free-text detail_desc via keyword matching)
Original plan (baggy/bootcut jeans, canvas jackets) was ABANDONED — those words barely 
exist in H&M's real vocab (baggy=2, bootcut=12, canvas=14 matches). Pivoted to 
evidence-based categories:
- Trouser fits: skinny_slim, tapered, straight, wide_relaxed, regular 
  (8,494 tagged, saved to data/interim/trousers_tagged.csv)
- Jacket styles: denim, leather_biker (leather+biker MERGED, heavy overlap), bomber 
  (843 tagged, saved to data/interim/jackets_tagged.csv)

## Notebooks
- 01_explore_articles.ipynb — Phase 1 tagging
- 02_build_timeseries.ipynb — Phase 2, DuckDB join → daily time series, saved to 
  data/processed/trousers_daily_sales.csv & jackets_daily_sales.csv
- 03_eda.ipynb — Phase 3 EDA (rolling averages, trend vs seasonality)
- 04_forecasting.ipynb — Phase 4 (all forecasting work; current notebook)

## Completed phases

### Phase 1: Tagging — DONE
Keyword-matched detail_desc into subcategories. Validated tagging logic with manual 
keyword frequency checks before committing.

### Phase 2: Time series — DONE
DuckDB inner join (transactions ⋈ tagged articles on article_id), grouped by date + 
category, counted units. trousers_ts (3670 rows), jackets_ts (2200 rows).

### Phase 3: EDA — DONE
Key findings via 30-day rolling averages:
- TROUSERS = TREND-dominated. skinny_slim declined ~55% in units sold but only ~35% in 
  distinct products sold → genuine demand decline, not just fewer styles stocked. 
  tapered & straight rose. wide_relaxed & regular small/flat.
- JACKETS = SEASONAL. denim & leather_biker peak every spring, trough every fall. 
  denim consistently outsells leather_biker. bomber small.

### Phase 4: Forecasting — DONE
Journey: naive baseline → moving avg → linear regression → gradient boosting → Prophet.
- Naive is very hard to beat on DAILY data (short-term persistence dominates).
- CAUGHT a bug: initial naive-vs-linear comparison used different time periods; fixed 
  so all models scored on identical held-out test set.
- Ruled out COVID as cause of linear underperformance (tested pre-COVID holdout, naive 
  still won) → real issue is models couldn't capture seasonality/spikes.
- Reframed to WEEKLY aggregation. Installed Prophet (yearly_seasonality=True).
- KEY METHODOLOGY INSIGHT: 1-week-ahead naive comparison is unfair (naive always has 
  last week's real value). Reran at realistic 4-WEEK-AHEAD horizon (supplier lead time).

## HEADLINE FINDING (Phase 4)
Built reusable function forecast_category_prophet(). Ran all 8 categories at 4-week-
ahead horizon. Prophet improvement % over naive:

JACKETS:
- denim: +42.0% (Prophet wins) — strong clean seasonality
- bomber: +16.2% (Prophet wins)
- leather_biker: -27.7% (naive wins) — messy BIMODAL seasonality (confirmed via 
  component plot: two peaks/year, small swing; likely the leather+biker merge)

TROUSERS:
- tapered: +37.5% (Prophet wins)
- straight: +39.4% (Prophet wins)
- skinny_slim: -17.5% (naive wins) — TREND-dominated not seasonal, so Prophet's 
  seasonal modeling adds little
- wide_relaxed: -88.0% (naive wins) — low volume (~1164/wk), noise dominates
- regular: -111.4% (naive wins) — very low volume (~491/wk)

**UNIFIED RULE: Prophet wins when a category has (a) adequate volume AND (b) genuine 
seasonality. Loses on low-volume (noisy) or trend-dominated series. → Recommend 
PER-CATEGORY MODEL SELECTION, not one-size-fits-all.**

Prophet component decomposition (denim) is a strong portfolio visual: trend (steady 
decline ~1030→600) + yearly seasonality (spring peak ~+930, Nov trough ~-600).

## NEXT: Phase 5 — Inventory policy
- [ ] For categories where we have a good forecast, translate forecast + forecast 
  uncertainty into inventory policy: safety stock = z * demand_std * sqrt(lead_time); 
  reorder point = avg demand over lead time + safety stock
- [ ] Use Prophet's uncertainty intervals (yhat_lower/yhat_upper) as the demand 
  variability input
- [ ] Simulate: forecast-driven policy vs naive policy → quantify reduction in 
  stockouts / excess inventory in $ terms
- [ ] Apply per-category model selection (Prophet for seasonal+high-volume, simpler 
  for others)

## Then Phase 6
- [ ] Streamlit dashboard + README writeup