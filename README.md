# TCGA-BRCA: MKI67 Expression Across Tumor Stages

**GitHub Repository:** [https://github.com/Setyhoseini/TCGA-BRCA-dataset-analysis.git](https://github.com/Setyhoseini/TCGA-BRCA-dataset-analysis.git)
**Course:** Statistics — Fall 1405  
**Project Path:** ب (TCGA-BRCA multi-omic)  
**Author:** Setayesh Hoseini  

## 1. Project Overview
This project investigates whether **MKI67** (a marker of cellular proliferation) mRNA expression is associated with AJCC pathologic tumor stage in breast cancer, and whether this association persists after adjusting for age at diagnosis. The analysis uses multi-omic data from The Cancer Genome Atlas (TCGA-BRCA), combining clinical data with RNA-seq gene expression.

## 2. Repository Structure
The repository follows standard data science reproducibility practices:

```text
├── README.md               # This file: project overview and setup
├── PROJECT_CARD.md         # Statistical framework, hypotheses, and variables
├── requirements.txt        # Python dependencies
├── data/
│   ├── README.md           # Data sources and reconstruction steps
│   ├── raw/                # Raw downloads (ignored by git)
│   └── processed/          # Clean analytic datasets (e.g., analysis_table.csv)
├── src/
│   ├── download_script.py  # Script to query GDC API and build manifest
│   └── verify_downloads.py # Script to verify MD5 checksums
├── notebooks/
│   └── 01_first_look.ipynb # Phase 1: Data audit, cleaning, and descriptive plots
├── figures/                # Saved plots from the notebook
└── reports/                # Phase outputs (PDF reports)
```

## 3. Environment Setup
To recreate the environment and run the code:

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/Scripts/activate  # On Windows Git Bash

# 2. Install dependencies
pip install -r requirements.txt
```

## 4. Data Reconstruction
Large raw data files (RNA-seq and clinical TSVs) are **not** committed to this repository due to size constraints. 
To download the data from the NCI Genomic Data Commons (GDC):
1. Run `python src/download_script.py` to generate the manifest.
2. Download the files using `gdc-client` (see instructions in `data/README.md`).

## 5. Phase 1 Status
- **Completed:** Clinical data audit (collapsed from 5,546 rows to 1,083 unique patients), RNA-seq barcode mapping, 6-gene panel extraction, and descriptive visualizations.
- **Notebook:** See `notebooks/01_first_look.ipynb` for the full analysis and outputs.
- **Results:** MKI67 expression does not increase monotonically with stage (Stage II shows the highest mean expression).