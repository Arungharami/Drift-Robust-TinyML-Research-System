"""Workspace bundling rules for `colab upload` (Mission 12).

This module only resolves *which files* belong in dist/colab_workspace.tar.gz; the archive
itself is built by scripts/colab/prepare_workspace.sh (`tar -czf ... -T <filelist>`) so the
include/exclude logic stays unit-testable without invoking tar or the Colab CLI.
"""
from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH, get_value, load_config

# Always excluded regardless of configs/colab.yaml, as a defense-in-depth backstop against
# accidentally bundling credentials/caches even if the config's exclude list is edited.
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
    rel_str = rel_path.as_posix()
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(rel_path.name, pattern):
            return True
    return False


def collect_workspace_files(root: Path, include: list[str], exclude_patterns: list[str]) -> list[Path]:
    """Return repo-relative file paths under `root` that belong in the workspace bundle.

    Missing `include` entries are skipped silently — not every optional path (e.g. tests/)
    must exist for the bundle to be valid.
    """
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


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.colab_control.workspace")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, type=Path)
    args = parser.parse_args()

    # On Windows, text-mode stdout translates "\n" -> "\r\n" even when redirected to a file;
    # the bash consumers of this output (prepare_workspace.sh's `tar -T`, build_release_bundle.sh's
    # `while read`) then see a trailing \r baked into every filename and fail to find the file.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="\n")

    config = load_config(args.config)
    include = get_value(config, "colab.workspace_include", [])
    exclude = get_value(config, "colab.workspace_exclude_patterns", [])
    for f in collect_workspace_files(args.root, include, exclude):
        print(f.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
