# pages/1_covariate_associations.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Covariate ↔ Wavelet (top-N per feature)")

# Use shared data
df_cov = st.session_state.df_cov

# Sidebar for filters (now per-page, but you can move to global if preferred)
p_max = st.sidebar.slider("Max p-value", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")
min_r = st.sidebar.slider("Minimum r value", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
top_n_covariates = st.sidebar.slider("Max number of covariates per feature", 1, 20, 5)

df_plot1 = df_cov[(df_cov['p_value'] < p_max) & (df_cov['r'] >= min_r)]

# Group by feature and take top N covariates by r for each feature
def top_n_per_group(group):
    return group.nlargest(top_n_covariates, 'r')

df_plot1 = df_plot1.groupby('feature').apply(top_n_per_group).reset_index(drop=True)

# Sort features by max r descending, and within feature by r descending
feature_max_r = df_plot1.groupby('feature')['r'].max().sort_values(ascending=False)
feature_order = feature_max_r.index

# Assign numerical y for spreading
feature_to_num = {f: i for i, f in enumerate(feature_order)}
df_plot1['y_num'] = df_plot1['feature'].map(feature_to_num)

# Spread points vertically within each feature
offsets = []
for _, group in df_plot1.groupby('feature'):
    n = len(group)
    if n > 1:
        offset = np.linspace(-0.4, 0.4, n)
    else:
        offset = [0]
    offsets.extend(offset)
df_plot1['y_num'] += offsets

df_plot1 = df_plot1.sort_values(['y_num', 'r'], ascending=[True, False])

# Plotly scatter for interactivity
fig1 = px.scatter(
    df_plot1,
    x='r',
    y='y_num',
    text='covariate',
    hover_data=['feature', 'covariate', 'p_value', 'r', 'neg_log10_p'],
    title="r Values by Wavelet Feature (Labeled with Covariate)"
)
fig1.update_traces(textposition='middle right')
fig1.update_layout(
    xaxis_title="Correlation coefficient (r)",
    yaxis_title="Wavelet Feature",
    yaxis=dict(
        tickmode='array',
        tickvals=list(range(len(feature_order))),
        ticktext=feature_order
    ),
    height=max(400, 30 * len(feature_order))  # Dynamic height
)

st.plotly_chart(fig1, use_container_width=True)
