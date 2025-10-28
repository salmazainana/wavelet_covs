# pages/4_sleep_prs_top_n.py
import streamlit as st
import pandas as pd

st.title("Sleep-PRS Top-N Significant Rows")

# Use shared data
df_sleep = st.session_state.df_sleep

# Sidebar for filter
nlargest_table = st.sidebar.slider("Top N by -log10(p)", 10, 200, 50)
p_max_table = st.sidebar.slider("Max p-value for table", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")

df_table = df_sleep[df_sleep['pval'] < p_max_table].nlargest(nlargest_table, 'neg_log10_p')

st.dataframe(df_table, use_container_width=True)
