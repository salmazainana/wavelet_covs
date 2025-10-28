import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Sleep-PRS ↔ Wavelet Volcano Plot")

# Use shared data
df_sleep = st.session_state.df_sleep

# Sidebar for filters
p_max_volc = st.sidebar.slider("Max p-value for this plot", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")
min_abs_corr = st.sidebar.slider("Minimum |correlation|", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
nlargest = st.sidebar.slider("Top N for r and -log10(p)", 10, 200, 100)

df_clean = df_sleep[(df_sleep['pval'] < p_max_volc) & (df_sleep['abs_corr'] >= min_abs_corr)]

# Top by r and top by -log10(p)
top_r = df_clean.nlargest(nlargest, "correlation")
top_p = df_clean.nlargest(nlargest, "neg_log10_p")

# Overlap
overlap = pd.merge(top_r, top_p, how="inner")

st.write(f"Number of overlapping points: {len(overlap)}")

# Plotly scatter for all points
fig2 = go.Figure()

# All associations
fig2.add_trace(go.Scatter(
    x=df_clean['correlation'],
    y=df_clean['neg_log10_p'],
    mode='markers',
    marker=dict(size=6, opacity=0.4, color='blue'),
    name='All associations',
    text=df_clean.apply(lambda row: f"Trait: {row['trait']}<br>Feature: {row['wave_feature']}<br>r: {row['correlation']}<br>p-value: {row['pval']}<br>-log10(p): {row['neg_log10_p']}", axis=1),
    hoverinfo='text'
))

# Overlap points (red, larger)
fig2.add_trace(go.Scatter(
    x=overlap['correlation'],
    y=overlap['neg_log10_p'],
    mode='markers+text',
    marker=dict(size=12, color='red'),
    name='Top overlapping points',
    text=overlap['wave_feature'] + '-' + overlap['trait'],
    textposition='top center',
    hovertext=overlap.apply(lambda row: f"Trait: {row['trait']}<br>Feature: {row['wave_feature']}<br>r: {row['correlation']}<br>p-value: {row['pval']}<br>-log10(p): {row['neg_log10_p']}", axis=1),
    hoverinfo='text'
))

fig2.update_layout(
    title="Top Sleep-PRS–Wavelet Associations: Strong and Highly Significant (p < 0.001)",
    xaxis_title="Correlation coefficient (r)",
    yaxis_title="-log10(p-value)",
    legend=dict(orientation='h'),
    height=600
)

st.plotly_chart(fig2, use_container_width=True)
