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

gdc_manifest_rnaseq.txt IS committed (small; reproducibility record).