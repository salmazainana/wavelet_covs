# pages/4_sleep_prs_volcano.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.title("Sleep-PRS ↔ Wavelet Volcano Plot")

# Use shared data
df = st.session_state.df_sleep

# Sidebar for filters
st.sidebar.header("Filters for Sleep Volcano")
p_max_global = st.sidebar.slider("Max p-value", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")
df_filtered = df[df['pval'] < p_max_global]

# Volcano Plot
st.header("r vs -log10(p-value) Volcano Plot")
st.write("Scatter plot of r vs -log10(p). Highlights overlap of top N by |r| and top N by -log10(p). Hover/click to see details.")

# Dynamic filter for plot (use p_max_global instead of hard 1e-3)
df_clean = df_filtered.copy()  # No additional hard filter

if df_clean.empty:
    st.warning("No data meets the p-value criteria.")
else:
    # Add abs_correlation for top by effect size
    df_clean['abs_correlation'] = abs(df_clean['correlation'])

    # Slider for nlargest
    nlargest = st.slider("Top N for |r| and -log10(p)", 10, 200, 100)

    # Top by |r| and top by -log10(p)
    top_r = df_clean.nlargest(nlargest, "abs_correlation")
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
        text=df_clean.apply(lambda row: f"Feature: {row['wave_feature']}<br>Trait: {row['trait']}<br>r: {row['correlation']}<br>p-value: {row['pval']}<br>-log10(p): {row['neg_log10_p']}", axis=1),
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
        hovertext=overlap.apply(lambda row: f"Feature: {row['wave_feature']}<br>Trait: {row['trait']}<br>r: {row['correlation']}<br>p-value: {row['pval']}<br>-log10(p): {row['neg_log10_p']}", axis=1),
        hoverinfo='text'
    ))

    fig2.update_layout(
        title=f"Top Wavelet–Sleep-PRS Associations (p < {p_max_global:.2e})",
        xaxis_title="Correlation coefficient (r)",
        yaxis_title="-log10(p-value)",
        legend=dict(orientation='h'),
        height=600
    )

    st.plotly_chart(fig2, use_container_width=True)

# Add table for top significant
st.header("Top Significant Associations")
top_n_table = st.slider("Top N for table (by -log10(p))", 10, 200, 50)
if not df_filtered.empty:
    top_table = df_filtered.nlargest(top_n_table, "neg_log10_p")[['trait', 'wave_feature', 'correlation', 'pval', 'neg_log10_p']]
    st.dataframe(top_table, use_container_width=True)
else:
    st.warning("No data for table.")
