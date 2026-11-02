# Data Sources and Reconstruction

This file documents every dataset used in the project, its origin, the date
of acquisition, and the exact steps required to reconstruct the analytic
dataset from the official source. It satisfies the reproducibility
requirement of the project document (§11).

---

## 1. Project and dataset

- **Project**: TCGA-BRCA — The Cancer Genome Atlas, Breast Invasive Carcinoma
- **Source**: NCI Genomic Data Commons (GDC) Data Portal
- **Portal URL**: https://portal.gdc.cancer.gov/
- **Project URL**: https://portal.gdc.cancer.gov/projects/TCGA-BRCA
- **Access type**: Open (no registration, no dbGaP approval required)

Two data types are used in this project:

1. **Clinical data** (patient-level)
2. **RNA-seq gene expression** (sample-level; must be mapped to patients)

Large raw files are **not** committed to this repository (see `.gitignore`).
The instructions below are sufficient to reconstruct every file.

---

## 2. Clinical data

### Acquisition
- **Date received**: 2026-10-31
- **Method**: Downloaded from the project page ("Clinical" download button)
- **Archive**: `clinical.project-tcga-brca.2026-10-31.tar.gz`
- **Extracted to**: `data/raw/clinical/`

### Files
data/raw/clinical/
├── clinical.tsv ← flattened, one row per case × diagnosis × treatment
├── exposure.tsv
├── family_history.tsv
├── follow_up.tsv
└── pathology_detail.tsv

### Structure as received
- `clinical.tsv`: **5,546 rows × 202 columns**
- Unique patients (`cases.case_id`): **1,098**
- Row explosion is **structural**:
  - Unique (case, diagnosis) pairs: **1,343**
  - Unique (case, treatment) pairs: **5,537**  ← this is what drives the row count
  - Therefore rows ≈ patients × treatments, not patients

### Missing-value convention
GDC encodes missing values as the literal string `"'--"` (with a leading
apostrophe), **not** `NaN`. All numeric columns must be coerced with
`pd.to_numeric(..., errors="coerce")` after replacing `"'--"` with `NA`.

### Boolean encoding
Boolean flags are stored as **lowercase** strings `"true"` / `"false"`.
All comparisons must be case-insensitive:
`df[col].astype(str).str.lower() == "true"`.

### Column naming
Columns are node-prefixed (`cases.*`, `demographic.*`, `diagnoses.*`,
`treatments.*`). The patient identifier is `cases.case_id` (UUID) or
`cases.submitter_id` (TCGA barcode prefix, e.g. `TCGA-XX-XXXX`).

---

## 3. Clinical data — collapse to patient level

### Rule (documented and reproducible)
The raw `clinical.tsv` is not one row per patient. To build a patient-level
table for analysis, apply these steps **in order**:

1. **Keep only primary-diagnosis rows**
   Filter: `diagnoses.diagnosis_is_primary_disease` (case-insensitive) == `"true"`.
   - Result: 4,946 rows, 1,096 unique patients.

2. **Drop all `treatments.*` columns (44 columns)**
   Treatments are the source of the row explosion. They are not needed for
   patient-level descriptors in Phase 1 and are excluded here. If treatment
   information is needed later, it must be re-aggregated per patient
   *before* merging.
   - Result: 4,946 rows × 158 columns.
   - Rows are now **exact duplicates** of the same primary diagnosis, one
     copy per treatment record of that patient.

3. **Collapse to one row per patient**
   `drop_duplicates(subset="cases.case_id", keep="first")` after sorting by
   `diagnoses.days_to_diagnosis` (numeric coercion applied first).
   - Result: **1,096 rows × 158 columns** — one unique row per patient.

### Exclusions
- **3 rows** had a missing primary-disease flag (`"'--"`), affecting
  **2 unique patients**. These 2 patients are **excluded** from the
  patient-level table because no primary diagnosis could be established.
- All exclusions are logged in the Phase-1 notebook (`01_first_look.ipynb`),
  Cells 4a–4b.

### Output
- **Saved to**: `data/processed/clinical_patient_level.csv`
- **Shape**: 1,096 rows × 158 columns
- **Key**: `cases.case_id` (unique)
- **Verification**: `patient["cases.case_id"].is_unique == True`

---

## 4. RNA-seq data

### Acquisition
- **Date received**: 2026-10-31
- **Method**: GDC API query (script: `download_script.py`) → manifest →
  `gdc-client download`
- **Manifest**: `gdc_manifest_rnaseq.txt` (committed to repo)
- **Manifest content**: 1,231 files, 5-column GDC format
  (`id`, `filename`, `md5`, `size`, `state`)

### Filters used in the query
project.project_id = TCGA-BRCA
data_category = Transcriptome Profiling
data_type = Gene Expression Quantification
experimental_strategy = RNA-Seq
analysis.workflow_type = STAR - Counts

### Reconstruction steps
```bash
# 1. Regenerate the manifest (equivalent to running download_script.py)
python download_script.py   # produces gdc_manifest_rnaseq.txt

# 2. Download all files listed in the manifest
mkdir -p data/raw/rnaseq
gdc-client download -m gdc_manifest_rnaseq.txt \
                    -d data/raw/rnaseq/ \
                    --retry-amount 10 --wait-time 5

# 3. Verify integrity against md5sums in the manifest
python verify_downloads.py