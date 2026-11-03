# Data Sources and Reconstruction

This file documents every dataset used in the project, its origin, the date of acquisition, and the exact steps required to reconstruct the analytic dataset from the official source.

## 1. Project and dataset
- **Project**: TCGA-BRCA — The Cancer Genome Atlas, Breast Invasive Carcinoma
- **Source**: NCI Genomic Data Commons (GDC) Data Portal
- **Portal URL**: https://portal.gdc.cancer.gov/
- **Access type**: Open (no registration required)

Two data types are used:
1. Clinical data (patient-level)
2. RNA-seq gene expression (sample-level; mapped to patients)

Large raw files are **not** committed. The instructions below reconstruct every file.

## 2. Clinical data
- **Date received**: 2026-10-31
- **Archive**: `clinical.project-tcga-brca.2026-10-31.tar.gz`
- **Extracted to**: `data/raw/clinical/`
- **Raw file used**: `clinical.tsv` (5,546 rows × 202 columns, 1,098 unique patients)
- **Row explosion**: Rows ≈ patients × treatments (5,537 unique case-treatment pairs).
- **Missing values**: Encoded as `"'--"` (not NaN).
- **Boolean flags**: Lowercase strings `"true"` / `"false"`.

## 3. Clinical data — collapse to patient level
Rule:
1. Keep rows with `diagnoses.diagnosis_is_primary_disease` (case-insensitive) == `"true"`. → 4,946 rows, 1,096 unique patients.
2. Drop all `treatments.*` columns (44 columns). → 4,946 rows × 158 columns.
3. Sort by `diagnoses.days_to_diagnosis`; `drop_duplicates(cases.case_id)`. → 1,096 rows × 158 columns.

**Exclusions**: 3 rows with missing primary-disease flag (`'--`) affected 2 unique patients; excluded.

**Output**: `data/processed/clinical_patient_level.csv` (1,096 × 158). Key: `cases.case_id` (unique).

## 4. RNA-seq data
- **Date received**: 2026-10-31
- **Method**: GDC API query (`src/download_script.py`) → manifest → `gdc-client download`.
- **Manifest**: `gdc_manifest_rnaseq.txt` (committed; 1,231 files).
- **Reconstruction steps**:
```bash
python src/download_script.py
mkdir -p data/raw/rnaseq
gdc-client download -m gdc_manifest_rnaseq.txt -d data/raw/rnaseq/ --retry-amount 10 --wait-time 5
python src/verify_downloads.py
```
- **File format**: TSV, 9 columns, ~60,000 genes, metadata starts with `#`.

## 5. RNA-seq sample sheet and data-flow (Path B, ب۲)
- **Sample sheet**: 1,231 files → 1,226 unique samples (5 duplicate aliquots) → 1,095 unique patients. Saved: `data/processed/sample_sheet.csv`.
- **Sample types**: Primary Tumor (1,111), Solid Tissue Normal (113), Metastatic (7).

### Data-flow table (Path B, ب۲)
| Step | Count |
|---|---|
| Clinical patients (processed) | 1,096 |
| RNA-seq unique patients | 1,095 |
| Patients in BOTH clinical & RNA-seq | 1,093 |
| Patients with exactly 1 primary tumor | 1,084 |
| **Final analytic sample** | **1,083** |

**Rule A (One-sample-per-patient)**: Use the single Primary Tumor sample. 
- Excluded: 11 patients with >1 primary tumor (reserved for Phase 5 sensitivity), 2 RNA-seq-only, 3 clinical-only.

## 6. Gene panel and analytic table
- **Gene panel**: ESR1, PGR, ERBB2, MKI67, PCNA, GAPDH (pre-justified, not data-selected).
- **Sanity checks**: GAPDH TPM min = 161 (all > 0). Missing TPM = 0.

**Analytic table**: `data/processed/analysis_table.csv`
- **Shape**: 1,083 rows × 172 columns (158 clinical + 15 expression - 1 redundant join key dropped).
- **Unit**: One row per patient. Key: `cases.case_id` (unique).
- **Merge**: `patient` INNER JOIN `expression` on `cases.case_id`, `validate="one_to_one"`, **0 rows lost**.

## 7. Phase 1 Descriptive Results (Task 9)
- Stage distributions: I=180, II=611, III=248, IV=20 (24 missing/unknown).
- log(MKI67) means: Stage I=2.93, II=3.21, III=3.07, IV=3.13.
- Early (I-II) vs Late (III-IV): 3.145 vs 3.078 (descriptive, no test).
- **Observation**: MKI67 expression does not increase monotonically with stage.