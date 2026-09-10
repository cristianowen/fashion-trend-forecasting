import streamlit as st
import pandas as pd

st.title("Fashion Demand Forecasting & Inventory Policy")

trouser_df = pd.read_csv('data/processed/trouser_policy_results.csv')
jacket_df = pd.read_csv('data/processed/jacket_policy_results.csv')

st.header("Trouser Categories")
st.dataframe(trouser_df)

st.header("Jacket Categories")
st.dataframe(jacket_df)

st.header("Policy Comparison: Our Policy vs. Naive Policy ($)")

import altair as alt

combined_df = pd.concat([trouser_df, jacket_df])

chart_data_long = combined_df.melt(
    id_vars='category',
    value_vars=['dollars_our_policy', 'dollars_naive_policy'],
    var_name='policy',
    value_name='dollars'
)

grouped_bar = alt.Chart(chart_data_long).mark_bar().encode(
    x=alt.X('category:N', title='Category'),
    y=alt.Y('dollars:Q', title='Safety Stock Value ($)'),
    color='policy:N',
    xOffset='policy:N'
).properties(height=400)

st.altair_chart(grouped_bar, use_container_width=True)

st.header("Explore a Category")

all_categories_df = pd.concat([trouser_df, jacket_df]).reset_index(drop=True)
selected_category = st.selectbox("Select a category", all_categories_df['category'])

row = all_categories_df[all_categories_df['category'] == selected_category].iloc[0]

st.write("Adjust assumptions:")
toggle_col1, toggle_col2 = st.columns(2)
with toggle_col1:
    selected_service_level = st.select_slider(
        "Service level", options=[90, 95, 99], value=95, format_func=lambda x: f"{x}%"
    )
with toggle_col2:
    selected_lead_time = st.slider("Lead time (weeks)", min_value=1, max_value=8, value=4)

z_lookup = {90: 1.28, 95: 1.65, 99: 2.33}
selected_z = z_lookup[selected_service_level]

live_safety_stock = round(selected_z * row['demand_std'] * (selected_lead_time ** 0.5))
live_reorder_point = round(row['avg_weekly_sales'] * selected_lead_time + live_safety_stock)

col1, col2, col3 = st.columns(3)
col1.metric("Avg Weekly Sales", f"{row['avg_weekly_sales']:,.0f} units")
col2.metric("Safety Stock", f"{live_safety_stock:,.0f} units")
col3.metric("Reorder Point", f"{live_reorder_point:,.0f} units")

st.write(f"**Demand Std Dev:** {row['demand_std']:,.1f} units/week")
st.write(f"**Prophet vs Naive:** {row['prophet_improvement_pct']}% improvement "
         f"({'Prophet wins' if row['prophet_improvement_pct'] > 0 else 'Naive wins'})")

import ast
import altair as alt

st.subheader(f"Forecast vs. Actual — {selected_category}")

dates = ast.literal_eval(row['plot_dates'])
actual = ast.literal_eval(row['plot_actual'])
prophet_pred = ast.literal_eval(row['plot_prophet_pred'])
naive_pred = ast.literal_eval(row['plot_naive_pred'])

# Use whichever method we actually trust for this category
use_prophet = row['prophet_improvement_pct'] > 0
chosen_pred = prophet_pred if use_prophet else naive_pred
method_name = "Prophet" if use_prophet else "Naive"

plot_df = pd.DataFrame({
    'date': dates * 2,
    'value': actual + chosen_pred,
    'series': ['Actual'] * len(dates) + [f'Predicted ({method_name})'] * len(dates)
})
plot_df['date'] = pd.to_datetime(plot_df['date'])

forecast_chart = alt.Chart(plot_df).mark_line(point=True).encode(
    x=alt.X('date:T', title='Week'),
    y=alt.Y('value:Q', title='Units Sold'),
    color='series:N'
).properties(height=400)

st.altair_chart(forecast_chart, use_container_width=True)