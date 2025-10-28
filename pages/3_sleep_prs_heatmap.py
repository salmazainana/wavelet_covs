import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Sleep-PRS ↔ Wavelet Heatmap")

# Use shared data
df_sleep = st.session_state.df_sleep

# Sidebar for options
metric = st.sidebar.radio("Heatmap metric", ["correlation", "-log10(p)"])
agg = st.sidebar.selectbox("Aggregation for duplicates", ["mean", "max"], index=1)
p_max_heat = st.sidebar.slider("Max p-value for heatmap", min_value=1e-10, max_value=0.05, value=0.001, step=1e-5, format="%.10f")

df_heat = df_sleep[df_sleep['pval'] < p_max_heat]

# Pivot table
val = 'correlation' if metric == "correlation" else 'neg_log10_p'
pivot = df_heat.pivot_table(index='wave_feature', columns='trait', values=val, aggfunc=agg).fillna(np.nan)

# Order rows by mean absolute value
row_means = pivot.abs().mean(axis=1).sort_values(ascending=False)
pivot = pivot.loc[row_means.index]

# Heatmap
fig_h, ax_h = plt.subplots(figsize=(12, max(8, len(pivot.index) * 0.3)))
sns.heatmap(pivot, cmap="coolwarm" if metric == "correlation" else "viridis", center=0 if metric == "correlation" else None,
            annot=True, fmt=".2f", linewidths=0.5, ax=ax_h)
ax_h.set_title(f"Heatmap of {metric} (agg: {agg})")
plt.tight_layout()

st.pyplot(fig_h)
