import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from math import log10


st.title("Wavelet-Covariate Associations Visualizer")

st.write(
    "This app visualizes associations from the wavelet energy data and the master.phe file. "
    "It provides two interactive plots: one for r values by wavelet feature with covariate labels, "
    "and a volcano plot for r vs -log10(p-value) with highlighted overlaps."
)
# Clean cache to ensure fresh data load
st.cache_data.clear()
csv_path = 'wavelet_master_covs_regressions_summary.csv'
df = pd.read_csv(csv_path)
# Preprocess: Add -log10(p_value), handle any inf/nan
df['neg_log10_p'] = -np.log10(df['p_value'].clip(lower=1e-300))  # Avoid log(0) issues
df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['r', 'p_value', 'neg_log10_p'])

# Sidebar for global filters
st.sidebar.header("Global Filters")
p_max_global = st.sidebar.slider("Max p-value for all plots", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")
df_filtered = df[df['p_value'] < p_max_global]

# First Plot: Wavelet on Y, r on X, with covariate names
st.header("Plot 1: r Values by Wavelet Feature with Covariate Labels")
st.write("Filtered to p < selected threshold and r >= min r. Shows up to top N covariates per feature, for all features with qualifying associations. Points are spread vertically within each feature for better label readability.")

# Additional filters for Plot 1
p_max_plot1 = st.slider("Max p-value for this plot", min_value=1e-10, max_value=p_max_global, value=0.001, step=1e-5, format="%.10f")
min_r_plot1 = st.slider("Minimum r value for this plot", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
top_n_covariates = st.slider("Max number of covariates per feature", 1, 20, 5)

df_plot1 = df_filtered[(df_filtered['p_value'] < p_max_plot1) & (df_filtered['r'] >= min_r_plot1)]

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
    height=max(400, 30 * len(feature_order))  # Dynamic height based on number of features
)

st.plotly_chart(fig1)

# Second Plot: Volcano-like Plot
st.header("Plot 2: r vs -log10(p-value) Volcano Plot")
st.write("Scatter plot of r vs -log10(p). Highlights overlap of top N by r and top N by -log10(p). Hover/click to see details.")

# Filter for this plot (p < 0.001 already from global, but ensure finite)
df_clean = df_filtered[df_filtered['p_value'] < 1e-3]

# Slider for nlargest
nlargest = st.slider("Top N for r and -log10(p)", 10, 200, 100)

# Top by r and top by -log10(p)
top_r = df_clean.nlargest(nlargest, "r")
top_p = df_clean.nlargest(nlargest, "neg_log10_p")

# Overlap
overlap = pd.merge(top_r, top_p, how="inner")

st.write(f"Number of overlapping points: {len(overlap)}")

# Plotly scatter for all points
fig2 = go.Figure()

# All associations
fig2.add_trace(go.Scatter(
    x=df_clean['r'],
    y=df_clean['neg_log10_p'],
    mode='markers',
    marker=dict(size=6, opacity=0.4, color='blue'),
    name='All associations',
    text=df_clean.apply(lambda row: f"Feature: {row['feature']}<br>Covariate: {row['covariate']}<br>r: {row['r']}<br>p-value: {row['p_value']}<br>-log10(p): {row['neg_log10_p']}", axis=1),
    hoverinfo='text'
))

# Overlap points (red, larger)
fig2.add_trace(go.Scatter(
    x=overlap['r'],
    y=overlap['neg_log10_p'],
    mode='markers+text',
    marker=dict(size=12, color='red'),
    name='Top overlapping points',
    text=overlap['feature'] + '-' + overlap['covariate'],
    textposition='top center',
    hovertext=overlap.apply(lambda row: f"Feature: {row['feature']}<br>Covariate: {row['covariate']}<br>r: {row['r']}<br>p-value: {row['p_value']}<br>-log10(p): {row['neg_log10_p']}", axis=1),
    hoverinfo='text'
))

fig2.update_layout(
    title="Top Wavelet–Covariate Associations: Strong and Highly Significant (p < 0.001)",
    xaxis_title="Correlation coefficient (r)",
    yaxis_title="-log10(p-value)",
    legend=dict(orientation='h'),
    height=600
)

st.plotly_chart(fig2)
