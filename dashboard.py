import streamlit as st
import pandas as pd

st.title("Fashion Demand Forecasting & Inventory Policy")

trouser_df = pd.read_csv('data/processed/trouser_policy_results.csv')
jacket_df = pd.read_csv('data/processed/jacket_policy_results.csv')

st.header("Trouser Categories")
st.dataframe(trouser_df)

st.header("Jacket Categories")
st.dataframe(jacket_df)