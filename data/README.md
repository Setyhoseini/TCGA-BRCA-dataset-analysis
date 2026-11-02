# Data Sources and Reconstruction

This file documents every dataset used in the project, its origin, the
date of acquisition, and the exact steps required to reconstruct the
analytic dataset from the official source.

## 1. Project and dataset
- Project: TCGA-BRCA — The Cancer Genome Atlas, Breast Invasive Carcinoma
- Source: NCI Genomic Data Commons (GDC) Data Portal
- Portal URL: https://portal.gdc.cancer.gov/
- Project URL: https://portal.gdc.cancer.gov/projects/TCGA-BRCA
- Access: Open (no registration required)

## 2. Clinical data
- Date received: 2026-10-31
- Archive: clinical.project-tcga-brca.2026-10-31.tar.gz
- Extracted to: data/raw/clinical/
- Raw file used: clinical.tsv (5,546 rows × 202 columns, 1,098 unique patients)
- Row explosion is structural: rows ≈ patients × treatments
  (5,537 unique case-treatment pairs).
- Missing values are the literal string "'--" (not NaN).
- Boolean flags are lowercase strings ("true"/"false").

## 3. Clinical data — collapse to patient level
Rule:
1. Keep rows with diagnoses.diagnosis_is_primary_disease (case-insensitive) == "true".
   → 4,946 rows, 1,096 unique patients.
2. Drop all treatments.* columns (44 columns; row-explosion driver).
   → 4,946 rows × 158 columns.
3. Sort by diagnoses.days_to_diagnosis; drop_duplicates(cases.case_id).
   → 1,096 rows × 158 columns, one row per patient.

Exclusions: 3 rows with missing primary-disease flag ('--) affected
2 unique patients; those 2 patients are excluded (no primary diagnosis
could be established).

Output: data/processed/clinical_patient_level.csv
  - Shape: 1,096 × 158
  - Key: cases.case_id (unique)
  - Verified: cases.case_id.is_unique == True

## 4. RNA-seq data
- Date received: 2026-10-31
- Method: GDC API query (download_script.py) → manifest → gdc-client download
- Manifest: gdc_manifest_rnaseq.txt (committed; 1,231 files, 5-column GDC format)
- Query filters:
    project.project_id        = TCGA-BRCA
    data_category             = Transcriptome Profiling
    data_type                 = Gene Expression Quantification
    experimental_strategy     = RNA-Seq
    analysis.workflow_type    = STAR - Counts
- Reconstruction:
    python download_script.py
    mkdir -p data/raw/rnaseq
    gdc-client download -m gdc_manifest_rnaseq.txt -d data/raw/rnaseq/ --retry-amount 10 --wait-time 5
    python verify_downloads.py
- On disk: data/raw/rnaseq/<file_id>/<file_id>.rna_seq.augmented_star_gene_counts.tsv
- Total .tsv files: 1,231 (verified; matches manifest)
- One file per sample (aliquot), not per patient.
- File format: TSV, 9 columns, ~60,000 genes, metadata lines start with "#".
  Columns: gene_id, gene_name, gene_type, unstranded, stranded_first,
           stranded_second, tpm_unstranded, fpkm_unstranded, fpkm_uq_unstranded.

## 5. Analytic dataset (Phase-1 output)
- File: data/processed/analysis_table.csv (to be produced in Block 3)
- Unit: one row per patient (cases.case_id)
- Contents: clinical variables + selected gene expression values

## 6. Not committed to the repository
Excluded via .gitignore (reconstructable from this README):
- data/raw/ (raw downloads)
- .venv/
- .ipynb_checkpoints/

## 7. RNA-seq sample sheet and data-flow (Phase 1, Block 2)

### Sample sheet
- Built from GDC API: https://api.gdc.cancer.gov/files
- 1,231 file records → 1,226 unique sample_ids (5 sample_ids have
  multiple aliquots) → 1,095 unique patients.
- Saved: data/processed/sample_sheet.csv

### Sample type breakdown
| sample_type | count |
|---|---|
| Primary Tumor | 1,111 |
| Solid Tissue Normal | 113 |
| Metastatic | 7 |

### Data-flow table (Path B, ب۲)
| Step | Count |
|---|---|
| Clinical patients (processed) | 1,096 |
| RNA-seq files (raw) | 1,231 |
| RNA-seq unique samples | 1,226 |
| RNA-seq unique patients | 1,095 |
| Patients in BOTH clinical & RNA-seq | 1,093 |
| Patients with ≥1 primary tumor | 1,095 |
| Patients with exactly 1 primary tumor | 1,084 |
| Final analytic sample (clinical ∩ exactly-1-primary-tumor) | ~1,083 |

### One-sample-per-patient rule (documented, Phase 1)
**Rule A**: Use the patient's single Primary Tumor sample.
- Patients with exactly 1 primary tumor: 1,084
- Patients with >1 primary tumor: 11 → **excluded** from Phase 1
  (documented; to be revisited as a Phase-5 sensitivity check using
  Rule B: keep earliest `diagnosis_id`).
- RNA-seq-only patients (no clinical): 2 → excluded
- Clinical-only patients (no RNA-seq): 3 → excluded
- **Final N ≈ 1,083**

### One-sample-per-sample rule (for the 5 duplicate files)
Sample_ids with multiple aliquot files: 5. Because the analytic unit is
the patient (one primary-tumor file per patient), this does not affect
the final sample. The first file per (case_id, sample_type) is retained
when duplicates occur.

### Saved artifacts
- data/processed/sample_sheet.csv          — 1,231 files → patient map
- data/processed/data_flow_table.csv       — ب۲ flow table
- data/processed/analysis_sample_list.csv  — final ~1,083 patients

## 8. Gene panel and analytic table (Phase 1, Block 3)

### Gene panel (pre-justified, not data-selected)
| Gene | Role |
|---|---|
| ESR1  | Estrogen receptor α — ER+ subtype |
| PGR   | Progesterone receptor — PR+ subtype |
| ERBB2 | HER2 — HER2+ subtype |
| MKI67 | Ki-67 proliferation marker |
| PCNA  | Alternative proliferation marker (Phase-5 sensitivity) |
| GAPDH | Housekeeping control (sanity check) |

### Extraction
For each patient's single Primary Tumor STAR-Counts file, extracted:
- `tpm_unstranded` (normalized expression)
- `unstranded` (raw counts)
Only 3 of 9 columns loaded per file (memory-safe).

### Sanity checks (all passed)
- Missing TPM per gene: 0 across all 6 genes (1,083 patients)
- GAPDH TPM min = 161 (all > 0; housekeeping passes)
- GAPDH TPM range: 161 – 18,447 (realistic variation)

### Analytic table
- File: `data/processed/analysis_table.csv`
- Shape: 1,083 rows × 173 columns (158 clinical + 15 expression)
- Unit: one row per patient
- Key: `cases.case_id` (unique; verified)
- Merge: `patient` INNER JOIN `expression` on `cases.case_id = case_id`,
  `validate="one_to_one"`, **0 rows lost**
- Saved artifacts:
  - `data/processed/expression_panel.csv` — 1,083 × 15
  - `data/processed/analysis_table.csv`    — 1,083 × 173