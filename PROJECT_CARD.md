# PROJECT_CARD

## 1. Provisional title
MKI67 (proliferation) expression across AJCC tumor stages in TCGA-BRCA,
and its robustness to age adjustment.

## 2. Dataset and subset used
- **Route**: ب (TCGA-BRCA multi-omic)
- **Exact files used**: 
  - Clinical: `data/raw/clinical/clinical.tsv` (GDC Data Portal, accessed 2026-10-31)
  - RNA-seq: 1,231 STAR-Counts gene expression files (GDC Data Portal, accessed 2026-10-31)
- **Subset**: Adults diagnosed with breast invasive carcinoma who contributed both a primary-tumor RNA-seq profile and valid clinical data in TCGA-BRCA (N = 1,083).

## 3. Main statistical question
Is MKI67 mRNA expression (proliferation marker) associated with AJCC
pathologic tumor stage in breast cancer, and does the association persist
after adjusting for age at diagnosis?

Two sub-questions:
  (a) Descriptive/association: is the mean log-MKI67 expression different
      across stages (or between early vs late stage)?
  (b) Adjusted: does the difference persist after controlling for age?

## 4. Unit of observation and interpretable population
- **Unit**: One patient (one row per `cases.case_id`). No patient appears more than once.
- **Population**: The results are interpretable for adults with primary breast invasive carcinoma represented in the TCGA-BRCA cohort. 
- **Note on repeated observations**: The 11 patients with >1 primary tumor were excluded in Phase 1 to preserve the independence assumption (will be revisited in Phase 5).

## 5. Primary variables and measurement scale
| Variable | Role | Scale | Source |
|---|---|---|---|
| `MKI67_tpm` (log1p) | Response (Y) | Continuous | RNA-seq, `tpm_unstranded` |
| `ajcc_pathologic_stage` | Explanatory (X1) | Ordinal (4 levels; also collapsed to binary early/late) | Clinical, `diagnoses.ajcc_pathologic_stage` |
| `age_at_index` (years) | Explanatory / confounder (X2) | Continuous | Clinical, `demographic.age_at_index` |
| `PCNA_tpm` (log1p) | Secondary response (sensitivity) | Continuous | RNA-seq |
| `GAPDH_tpm` | Sanity check (not a response) | Continuous | RNA-seq |

## 6. Role of variables
- **Response (Y)**: `log1p(MKI67_tpm)` — positive, right-skewed raw TPM → log transform makes the distribution approximately normal, required for linear models.
- **Primary explanatory (X1)**: AJCC pathologic stage.
  - Two versions will be used:
    - 4-level ordinal: Stage I, II, III, IV (for ANOVA / regression with dummy coding).
    - 2-level binary: Early (I–II) vs Late (III–IV) (for two-sample tests and clear effect size).
- **Covariate (X2)**: Age at diagnosis in years.
- **Sanity control**: GAPDH (should not vary strongly by stage; if it does, that's a batch/quality flag).

## 7. Type of question
- **Primary**: Association (MKI67 vs stage).
- **Secondary**: Adjusted association (control for age).
- Not a prediction question. Not a causal question. The data is observational; no causal claim is possible or attempted.

## 8. Primary hypotheses
- **H0 (main)**: mean log1p(MKI67_tpm) is equal across stage groups.
- **H1 (main)**: mean log1p(MKI67_tpm) differs between at least two stage groups (two-sided).
- **H0 (adjusted)**: the coefficient on stage in `log1p(MKI67_tpm) ~ stage + age` equals 0.
- **H1 (adjusted)**: the coefficient on stage is not 0 after age adjustment.

Significance level α = 0.05. Effect sizes (Cohen's d / partial R²) reported alongside p-values per the course's requirement that significance be paired with magnitude.

## 9. Primary limitations
- **Sampling / Population**: This is a convenience sample of US cancer-center patients (TCGA), not a population-representative sample. The race distribution is overwhelmingly White.
- **Missing Data**: Some patients have missing pathological stage (24 patients had no valid stage and were excluded from stage-specific analyses).
- **Subgroup Size**: Stage IV has a very small sample size (n = 20), which limits statistical power and increases uncertainty for that specific group.
- **Observational Data**: Associations do not prove causation.

## 10. What this project is NOT
- Not a multi-gene or pathway-level screen (would require pre-registered feature sets + multiple-testing correction; outside the scope here).
- Not a survival analysis (survival models not covered in this course).
- Not a claim of causality.

## 11. Plan across phases (Roadmap)
- **Phase 1**: Descriptive (distribution of MKI67, stage, age; boxplots; one descriptive comparison — no inference yet).
- **Phase 2**: Probability framing ("P(high MKI67) by stage", conditional probability, independence check as an argument — not a formal test).
- **Phase 3**: Two-sample test (early vs late), ANOVA across 4 stages, CI on the difference, effect size, bootstrap CI on the mean MKI67.
- **Phase 4**: Simple linear regression (MKI67 ~ stage_binary), multiple regression (MKI67 ~ stage + age), residual diagnostics, check for outliers / influence.
- **Phase 5**: Sensitivity to (a) gene (MKI67 → PCNA), (b) stage grouping (4-level vs 2-level), (c) outliers / influence, (d) multi-primary-tumor patients re-included.