"""Secret scanning for the research bridge (Mission 27).

Two layers, deliberately simple and conservative (false positives are cheap; a missed
credential is not):

1. Filename deny-list — files that should never be staged for a release bundle or repo,
   regardless of content (kaggle.json, .env, *.pem, *.key, access_token, token.json caches).
2. Content pattern scan — known token prefixes/formats (GitHub, Hugging Face) and
   `KEY=value`-shaped assignments for the specific env var names this project uses, but only
   when a real-looking value follows (not `$VAR`, `${VAR}`, or an empty/placeholder string) —
   so documentation that merely *mentions* `HF_TOKEN` does not trigger a false positive.

Never logs or returns the secret value itself — only that a match occurred, its category, and
its location.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DENYLISTED_FILENAMES = frozenset(
    {
        "kaggle.json",
        "access_token",
        ".env",
        "token.json",
        "credentials.json",
        "id_rsa",
        "id_ed25519",
    }
)
DENYLISTED_SUFFIXES = frozenset({".pem", ".key"})

# (category, compiled pattern). Patterns match the *token itself*, not just its name, so a
# comment like "set HF_TOKEN in your environment" does not false-positive.
_TOKEN_VALUE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
]

# ENV_NAME=<real-looking value> — value must not be a shell reference or obviously a placeholder.
_ENV_ASSIGNMENT_NAMES = ("GH_TOKEN", "HF_TOKEN", "KAGGLE_API_TOKEN")
_PLACEHOLDER_VALUES = {"", "xxx", "changeme", "your_token_here", "<token>", "***"}


def _env_assignment_patterns() -> list[tuple[str, re.Pattern]]:
    patterns = []
    for name in _ENV_ASSIGNMENT_NAMES:
        patterns.append((f"{name.lower()}_assignment", re.compile(rf"\b{name}\s*=\s*(\S+)")))
    return patterns


_ENV_PATTERNS = _env_assignment_patterns()


@dataclass(frozen=True)
class SecretFinding:
    category: str
    location: str  # file path or a caller-supplied label; never the secret value itself


def _looks_like_placeholder(value: str) -> bool:
    stripped = value.strip("'\"")
    if stripped in _PLACEHOLDER_VALUES:
        return True
    if stripped.startswith("$"):  # $VAR or ${VAR} — a shell reference, not a literal secret
        return True
    return False


def scan_text(text: str, location: str = "<text>") -> list[SecretFinding]:
    """Scan a string for embedded credential-shaped content. Never returns the value found."""
    findings: list[SecretFinding] = []
    for category, pattern in _TOKEN_VALUE_PATTERNS:
        if pattern.search(text):
            findings.append(SecretFinding(category=category, location=location))
    for category, pattern in _ENV_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(1)
            if not _looks_like_placeholder(value):
                findings.append(SecretFinding(category=category, location=location))
    return findings


def is_denylisted_filename(path: Path) -> bool:
    return path.name in DENYLISTED_FILENAMES or path.suffix in DENYLISTED_SUFFIXES


def scan_path(root: Path, max_file_bytes: int = 2_000_000) -> list[SecretFinding]:
    """Walk `root` and report filename hits plus content hits in small text files.

    Binary/large files are skipped for content scanning (filename check still applies to them).
    """
    root = Path(root)
    findings: list[SecretFinding] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if is_denylisted_filename(p):
            findings.append(SecretFinding(category="denylisted_filename", location=rel))
            continue
        try:
            if p.stat().st_size > max_file_bytes:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        findings.extend(scan_text(text, location=rel))
    return findings
