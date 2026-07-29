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

## Next steps (Phase 2)
- [ ] Join tagged articles against transactions_train.csv using DuckDB
- [ ] Build daily/weekly demand time series per subcategory
- [ ] Save aggregated time series to data/processed/

## Files
- `notebooks/01_explore_articles.ipynb` — Phase 1 (tagging)
- `notebooks/02_build_timeseries.ipynb` — Phase 2 (in progress)
- `data/interim/trousers_tagged.csv`, `data/interim/jackets_tagged.csv` — tagged data 
  (not on GitHub, regenerate by rerunning notebook 01)