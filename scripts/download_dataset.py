"""Download the official dataset without overwriting prior evidence."""
from pathlib import Path
from src.data.download import download_dataset

if __name__ == "__main__":
    result = download_dataset(Path("data/raw"), Path("data/manifests/dataset_manifest.json"))
    print(f"Downloaded {result['archive']} SHA-256={result['archive_sha256']}")
