"""Validate downloaded chronological batches and stop on invalid evidence."""
from pathlib import Path
from src.data.validation import validate_dataset

if __name__ == "__main__":
    report = validate_dataset(Path("data/raw"), Path("results/reproducibility/dataset_validation.json"), Path("results/reproducibility/dataset_validation.md"))
    print(report)
    if report["status"] != "COMPLETED": raise SystemExit("Dataset validation failed; experiments are stopped.")
