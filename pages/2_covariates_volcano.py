# pages/2_covariates_volcano.py - Fixed syntax (removed any invisible chars, proper imports)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

df = st.session_state.df_cov

# Sidebar for global filters
st.sidebar.header("Global Filters")
p_max_global = st.sidebar.slider("Max p-value for all plots", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")
df_filtered = df[df['p_value'] < p_max_global]

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
