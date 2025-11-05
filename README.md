
# 🌊 Wavelet ↔ Sleep-PRS & LDSC Visualizer

An interactive Streamlit dashboard to explore associations between wavelet-derived ECG features, sleep-related PRS (polygenic risk scores), and genetic correlations (LDSC).

This app integrates multiple statistical analyses and visual tools to help interpret the relationship between genetic data and ECG wavelet phenotypes.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

# Repository Structure
```text
pages/
├─ 1_covariate_associations.py      # Exploratory covariate regressions
├─ 2_covariates_volcano.py          # Volcano plot for covariate associations
├─ 3_sleep_ldsc_volcano.py          # LDSC genetic correlation analysis
├─ 4_sleep_prs_volcano.py           # Sleep-PRS ↔ wavelet regressions
streamlit_app.py                    # Main interactive app
data/
├─ wavelet_dedup_new.phe            # Wavelet-transformed ECG features
├─ summary_wavelet_sleepPRS.csv     # Sleep-PRS regression summary
├─ rg_summary_all.tsv                # LDSC results
```
## 1. Covariate Associations (pages/1_covariate_associations.py)

Exploratory regressions of wavelet features on covariates.

> Details later.

---

## 2. Covariates Volcano (pages/2_covariates_volcano.py)

Volcano plot visualization for covariate associations.

> Details later.

---
## 3. LDSC Genetic Correlation (pages/3_sleep_ldsc_volcano.py)

### Input Data
- `rg_summary_all.tsv`  
  Contains **genetic correlations** \( r_g \), standard errors, z-scores, p-values, and heritabilities for wavelet features vs sleep traits.
- Data generated using **LDSC**.

### Mathematical Model
For each pair of sumstats.gz file \((y, x)\) of wavelet feature \(y\) and sleep trait \(x\):

\[
\hat{r}_g = \frac{\mathrm{cov}_g(y, x)}{\sqrt{\mathrm{h^2_x}_SNP \cdot \mathrm{h^2_y}_SNP}}
\]

where \(\mathrm{cov}_g\), \mathrm{h^2_x}_SNP and \(\mathrm{h^2_y}_SNP\) are **genetic covariance** and **SNP-based heritabilties** of \(x\) and \(y\) respectively, estimated from summary statistics.

### Visualization
- Volcano plot: \(\hat{r}_g\) vs \(-\log_{10}(p)\)
- Highlight top overlapping points by absolute \(|r_g|\) and significance (\(p < 0.05\)).

---

## 4. Sleep-PRS ↔ Wavelet Regressions (pages/4_sleep_prs_volcano.py)

### Input Data
- **Wavelet features:** `wavelet_dedup_new.phe`  
  - Discrete wavelet transform (Daubechies 6, levels 1–6) applied to ECG leads.
  - Energy at each level computed as features:

\[
E_{\text{level k}} = \sum_i (c_{k,i})^2
\]

where \(c_{k,i}\) are wavelet coefficients at level \(k\).

- **Sleep PRS:** computed via PLINK2 using GWAS-derived weights:

```bash
plink2 \
  --bfile ukb24983_cal_hla_cnv \
  --score trait_weights.tsv 2 4 6 header-read cols=+scoresums \
  --out <OUT_DIR>/<trait>_PRS.sscore
```

- **Covariates:** age, sex, top 10 principal components (`master.phe`).

### Preprocessing
1. Merge wavelet features, covariates, and PRS per individual.
2. Residualize wavelet features against covariates:

\[
\tilde{y} = y - (\beta_0 + \beta_1 \cdot \text{age} + \beta_2 \cdot \text{sex} + \sum_{i=1}^{10} \beta_{2+i} \cdot \text{PC}_i)
\]

3. Standardize residualized features to mean 0 and variance 1.

### Regression Model
For each residualized and standardized \(y\) and PRS \(x\):

\[
\tilde{y}_i = \alpha + \gamma \cdot x_i + \epsilon_i, \quad \epsilon_i \sim \mathcal{N}(0, \sigma^2)
\]

- \(\gamma\) = effect of PRS on wavelet feature.
- Compute correlation \(r\) and significance \(p\)-value:


### Visualization
- **Volcano plot:** correlation \(r\) vs \(-\log_{10}(p)\) for PRS regressions.
- **Highlight:** top overlapping points by \(|r|\) and \(-\log_{10}(p)\).
- **Volcano plot:** LDSC genetic correlation \(r_g\) vs \(-\log_{10}(p)\), highlighting significant correlations (\(p<0.05\)).

---

## Streamlit App
Launch the interactive visualizer:

```bash
streamlit run streamlit_app.py
```

## Navigate between pages via sidebar:

- Covariate Associations (pages 1–2)

- Sleep-PRS Visualizations (pages 3–4)

## References

- Bulik-Sullivan et al., Nat Genet, 2015 — LD Score Regression
