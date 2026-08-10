"""Non-destructive official UCI dataset acquisition with an evidence manifest."""
from __future__ import annotations
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests
from src.utils.hashing import sha256_file

SOURCE_URL = "https://archive.ics.uci.edu/static/public/224/gas+sensor+array+drift+dataset.zip"

def download_dataset(raw_dir: Path, manifest_path: Path, source_url: str = SOURCE_URL) -> dict:
    raw_dir.mkdir(parents=True, exist_ok=True); manifest_path.parent.mkdir(parents=True, exist_ok=True)
    archive = raw_dir / "gas_sensor_array_drift_dataset.zip"
    if archive.exists():
        raise FileExistsError(f"Refusing to replace existing archive: {archive}")
    temporary = archive.with_suffix(".zip.part")
    try:
        with requests.get(source_url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with temporary.open("wb") as handle:
                shutil.copyfileobj(response.raw, handle)
        temporary.replace(archive)
        extract_dir = raw_dir / "extracted"
        if extract_dir.exists(): raise FileExistsError(f"Refusing to replace: {extract_dir}")
        with zipfile.ZipFile(archive) as zf: zf.extractall(extract_dir)
    finally:
        if temporary.exists(): temporary.unlink()
    files = [{"path": str(p.relative_to(raw_dir)), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(raw_dir.rglob("*")) if p.is_file()]
    manifest = {"source_url": source_url, "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                "archive": str(archive), "archive_sha256": sha256_file(archive), "files": files}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
