# Fashion Demand Forecasting & Inventory Policy

Forecasts weekly demand for fashion subcategories (jean fits, jacket styles) using 
the H&M Personalized Fashion Recommendations dataset, then translates those 
forecasts into inventory policy recommendations — safety stock and reorder points.

**[Live dashboard screenshot / demo link — add once deployed]**

## The problem

Retailers need to decide how much buffer inventory to hold for each product 
category. Too little risks stockouts; too much ties up cash. This project builds 
a forecasting pipeline that estimates demand uncertainty per category and uses it 
to right-size that buffer — rather than applying a single blanket policy across 
very different product types.

## Key findings

- **No single forecasting model wins everywhere.** Prophet beat a naive 
  (persistence) baseline on high-volume, seasonal categories (denim, bomber, 
  tapered, straight fit) but lost on trend-dominated or low-volume categories 
  (skinny slim, wide/relaxed, regular fit, leather/biker jackets).
- Applied **per-category model selection** for demand uncertainty estimation: 
  Prophet's confidence intervals where Prophet wins, trend-adjusted historical 
  variability (rolling-residual method) where naive wins.
- **Result: a 39.5% reduction in required safety stock capital** (~$275,000 on a 
  $15/unit cost assumption) compared to a naive, one-size-fits-all policy — 
  without lowering the target service level.

## Methodology

1. Tagged ~8,500 trouser and ~850 jacket products into subcategories from raw 
   product descriptions (evidence-based, not assumed — pivoted away from 
   categories that barely existed in the real data).
2. Built weekly time series per category via a DuckDB join over 31.8M transaction 
   rows.
3. Compared naive, linear regression, gradient boosting, and Prophet forecasts at 
   a realistic 4-week-ahead horizon (matching typical supplier lead time).
4. Converted forecast uncertainty into safety stock (`z × demand_std × √lead_time`) 
   and reorder point, with the demand_std source chosen per category based on 
   which model actually fit that category's pattern.
5. Simulated dollar impact vs. a naive baseline policy.

## Tech stack

Python · pandas · DuckDB · Prophet · scikit-learn · Altair · Streamlit

## Running it

```bash
git clone https://github.com/cristianowen/fashion-trend-forecasting.git
cd fashion-trend-forecasting
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Data isn't included in this repo (see `.gitignore`) — download the 
[H&M dataset](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) 
from Kaggle and place it in `data/raw/`. Then run the notebooks in order 
(`01` through `04`) to regenerate the processed data, and launch the dashboard:

```bash
streamlit run dashboard.py
```

## Project structure

```
notebooks/       # Analysis pipeline, run in numeric order
dashboard.py      # Interactive Streamlit dashboard
data/             # Gitignored — regenerate via notebooks
PROGRESS.md        # Development log / session handoff notes
```