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

## Next steps (Phase 4 — Forecasting)
- [ ] Choose forecasting approach per category type (trend-dominant vs seasonal-dominant)
- [ ] Build baseline models, then compare against ML approaches (XGBoost/LightGBM)
- [ ] Evaluate with MAPE/RMSE against baseline

## Files
- `notebooks/01_explore_articles.ipynb` — Phase 1 (tagging)
- `notebooks/02_build_timeseries.ipynb` — Phase 2 (in progress)
- `data/interim/trousers_tagged.csv`, `data/interim/jackets_tagged.csv` — tagged data 
  (not on GitHub, regenerate by rerunning notebook 01)