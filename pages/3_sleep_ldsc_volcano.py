import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.title("LDSC Genetic Correlation Volcano Plot")

df = st.session_state.df_ldsc_sleep

# Preprocessing
df['neg_log10_p'] = -np.log10(df['p'])
df['abs_rg'] = abs(df['rg'])

# Sidebar filters
st.sidebar.header("Filters for LDSC Volcano")
p_max = st.sidebar.slider("Max p-value", min_value=1e-10, max_value=0.05, value=0.05, step=1e-5, format="%.10f")
df_filtered = df[df['p'] < p_max]

# Volcano plot
st.header("rg vs -log10(p-value)")
st.write("Visualizes genetic correlations (rg) and their significance from LDSC analysis.")
if df_filtered.empty:
    st.warning("No data meets the p-value criteria.")
else:
    top_n = st.slider("Top N by |rg| and significance", 5, 100, 20)

    top_rg = df_filtered.nlargest(top_n, "abs_rg")
    top_p = df_filtered.nlargest(top_n, "neg_log10_p")
    overlap = pd.merge(top_rg, top_p, how="inner")

    fig = go.Figure()

    # All points
    fig.add_trace(go.Scatter(
        x=df_filtered['rg'],
        y=df_filtered['neg_log10_p'],
        mode='markers',
        marker=dict(size=6, opacity=0.5, color='cornflowerblue'),
        name='All results',
        text=df_filtered.apply(lambda row: f"Trait: {row['trait']}<br>Feature: {row['wave_feature']}<br>rg: {row['rg']:.3f}<br>p={row['p']:.3e}", axis=1),
        hoverinfo='text'
    ))

    # Overlap points
    fig.add_trace(go.Scatter(
        x=overlap['rg'],
        y=overlap['neg_log10_p'],
        mode='markers+text',
        marker=dict(size=12, color='crimson'),
        name='Top overlapping',
        text=overlap['trait'] + '–' + overlap['wave_feature'],
        textposition='top center'
    ))


    fig.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="gray")
    fig.add_vline(x=0, line_color="black")

    fig.update_layout(
        title=f"LDSC rg vs -log10(p-value) (p < {p_max:.1e})",
        xaxis_title="Genetic correlation (rg)",
        yaxis_title="-log10(p-value)",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )

    st.plotly_chart(fig, use_container_width=True)

# Table of top significant correlations
st.header("Top Significant Genetic Correlations")
n_table = st.slider("Number of rows to display", 10, 200, 50)
if not df_filtered.empty:
    top_table = df_filtered.nlargest(n_table, "neg_log10_p")[['trait', 'wave_feature', 'rg', 'p', 'neg_log10_p']]
    st.dataframe(top_table, use_container_width=True)
else:
    st.warning("No significant results available.")



