from pathlib import Path
import pytest
from src.data.validation import validate_dataset
def test_missing_real_dataset_stops(tmp_path: Path):
    with pytest.raises(FileNotFoundError): validate_dataset(tmp_path,tmp_path/"v.json",tmp_path/"v.md")
