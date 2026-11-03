import requests
import json

url = "https://api.gdc.cancer.gov/files"

filters = {
    "op": "and",
    "content": [
        {"op": "in", "content": {"field": "cases.project.project_id", "value": ["TCGA-BRCA"]}},
        {"op": "in", "content": {"field": "data_category", "value": ["Transcriptome Profiling"]}},
        {"op": "in", "content": {"field": "data_type", "value": ["Gene Expression Quantification"]}},
        {"op": "in", "content": {"field": "experimental_strategy", "value": ["RNA-Seq"]}},
        {"op": "in", "content": {"field": "analysis.workflow_type", "value": ["STAR - Counts"]}}
    ]
}

params = {
    "filters": json.dumps(filters),
    "format": "JSON",
    "size": "10000",
    # Request the five fields required by gdc-client
    "fields": "file_id,file_name,md5sum,file_size,state"
}

response = requests.get(url, params=params)
response.raise_for_status()
files = response.json()['data']['hits']

# Write the proper 5-column manifest (tab-separated)
with open("gdc_manifest_rnaseq.txt", "w") as f:
    # Optional but recommended: write a header row
    f.write("id\tfilename\tmd5\tsize\tstate\n")
    for file in files:
        f.write(f"{file['file_id']}\t{file['file_name']}\t{file['md5sum']}\t{file['file_size']}\t{file['state']}\n")

print(f"Valid manifest created with {len(files)} files.")