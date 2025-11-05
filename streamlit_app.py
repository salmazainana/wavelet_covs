# streamlit_app.py (main entry point)
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Wavelet Visualizer", layout="wide")
st.title("Wavelet ↔ Covariate / Sleep-PRS / LDSC Explorer")

st.write("""
Welcome! Use the sidebar to navigate to specific visualizations.
- Data from: wavelet_master_covs_regressions_summary.csv, summary_wavelet_sleepPRS.csv, and LDSC results.
- Adjust filters in each page as needed.
""")

# Clean cache to ensure fresh data load
st.cache_data.clear()

# ===============================
# 🔹 Global data loading
# ===============================

# --- Covariate regressions ---
if "df_cov" not in st.session_state:
    csv_path_cov = 'wavelet_master_covs_regressions_summary.csv'
    df_cov = pd.read_csv(csv_path_cov)
    df_cov['neg_log10_p'] = -np.log10(df_cov['p_value'].clip(lower=1e-300))
    df_cov = df_cov.replace([np.inf, -np.inf], np.nan).dropna(subset=['r', 'p_value', 'neg_log10_p'])
    st.session_state.df_cov = df_cov

# --- Sleep-PRS regressions ---
if "df_sleep" not in st.session_state:
    csv_path_sleep = 'summary_wavelet_sleepPRS.csv'
    df_sleep = pd.read_csv(csv_path_sleep)
    df_sleep['neg_log10_p'] = -np.log10(df_sleep['pval'].clip(lower=1e-300))
    df_sleep['abs_corr'] = df_sleep['correlation'].abs()
    df_sleep = df_sleep.replace([np.inf, -np.inf], np.nan).dropna(subset=['correlation', 'pval', 'neg_log10_p'])
    st.session_state.df_sleep = df_sleep

# --- LDSC results ---
if "df_ldsc_sleep" not in st.session_state:
    csv_path_ldsc = 'rg_summary_all.csv'  # adjust to your repo path
    df_ldsc_sleep = pd.read_csv(csv_path_ldsc, sep="\t")
    df_ldsc_sleep['neg_log10_p'] = -np.log10(df_ldsc_sleep['p'].clip(lower=1e-300))
    df_ldsc_sleep['abs_rg'] = df_ldsc_sleep['rg'].abs()
    df_ldsc_sleep = df_ldsc_sleep.replace([np.inf, -np.inf], np.nan).dropna(subset=['rg', 'p', 'neg_log10_p'])
    st.session_state.df_ldsc_sleep = df_ldsc_sleep

# ===============================
# 🔹 Navigation setup
# ===============================
pg = st.navigation({
    "Covariate Associations": [
        st.Page("pages/1_covariate_associations.py"),
        st.Page("pages/2_covariates_volcano.py")
    ],
    "Sleep-PRS Visualizations": [
        st.Page("pages/4_sleep_prs_volcano.py"),
        st.Page("pages/3_sleep_ldsc_volcano.py"),
    ]
}, position="sidebar")

pg.run()

