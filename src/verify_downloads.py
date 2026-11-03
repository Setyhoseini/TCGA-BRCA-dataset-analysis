import hashlib
import os
import csv

MANIFEST_FILE = "gdc_manifest_rnaseq.txt"
DOWNLOAD_DIR = "data/raw/rnaseq"

def md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

missing = []
corrupt = []

with open(MANIFEST_FILE, "r") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        file_id = row["id"]
        expected_md5 = row["md5"]
        # The downloaded file is inside a subfolder named by its UUID
        filepath = os.path.join(DOWNLOAD_DIR, file_id, row["filename"])

        if not os.path.exists(filepath):
            missing.append((file_id, row["filename"]))
        else:
            actual_md5 = md5(filepath)
            if actual_md5 != expected_md5:
                corrupt.append((file_id, row["filename"]))

print(f"Total files in manifest: {len(missing) + len(corrupt) + (1231 - len(missing) - len(corrupt))}")
print(f"Missing files: {len(missing)}")
print(f"Corrupted files: {len(corrupt)}")

if missing:
    print("\n--- MISSING FILES (first 5) ---")
    for fid, fname in missing[:5]:
        print(f"  {fid}  {fname}")

if corrupt:
    print("\n--- CORRUPTED FILES (first 5) ---")
    for fid, fname in corrupt[:5]:
        print(f"  {fid}  {fname}")