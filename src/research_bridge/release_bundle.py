"""Release-bundle include/exclude resolution for dist/research_bridge/ (Mission 17).

Same split as src/colab_control/workspace.py: this module only resolves *which files* belong
in the bundle (unit-testable), the archive step itself lives in scripts/bridge/build_release_bundle.sh.
Every candidate file is also checked against src/research_bridge/secrets.py's denylist so a
credential file can never end up in a release bundle even if it were mistakenly added to
`include`.
"""
from __future__ import annotations

import fnmatch
from pathlib import Path

from .secrets import is_denylisted_filename

ALWAYS_EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".venv",
    ".python",
    ".pytest_cache",
    ".pytest_tmp",
    ".ipynb_checkpoints",
}


def is_excluded(rel_path: Path, exclude_patterns: list[str]) -> bool:
    if any(part in ALWAYS_EXCLUDED_DIR_NAMES for part in rel_path.parts):
        return True
    if is_denylisted_filename(rel_path):
        return True
    rel_str = rel_path.as_posix()
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(rel_path.name, pattern):
            return True
    return False


def collect_release_files(root: Path, include: list[str], exclude_patterns: list[str]) -> list[Path]:
    root = Path(root)
    files: list[Path] = []
    for entry in include:
        target = root / entry
        if target.is_file():
            rel = target.relative_to(root)
            if not is_excluded(rel, exclude_patterns):
                files.append(rel)
        elif target.is_dir():
            for p in sorted(target.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(root)
                    if not is_excluded(rel, exclude_patterns):
                        files.append(rel)
    return files
