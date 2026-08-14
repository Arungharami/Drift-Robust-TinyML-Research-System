"""Parse already-captured CLI output into platform status (Missions 3, 5, 10, 18).

Nothing here shells out — callers capture `gh auth status` / `hf auth whoami` / `kaggle ...`
output themselves and pass the text in, which keeps this module testable without live CLIs or
network access. Never returns or logs a token value.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

READY = "READY"
BLOCKED = "BLOCKED"
NOT_CONFIGURED = "NOT_CONFIGURED"
NOT_EXECUTED = "NOT_EXECUTED"
FAILED = "FAILED"
VALID_STATUSES = frozenset({READY, BLOCKED, NOT_CONFIGURED, NOT_EXECUTED, FAILED})

_GH_ACCOUNT_RE = re.compile(r"Logged in to \S+ account (\S+)")
_HF_WHOAMI_RE = re.compile(r"^([\w.\-]+)$", re.MULTILINE)


@dataclass(frozen=True)
class GithubAuthResult:
    authenticated: bool
    account: str | None


def parse_gh_auth_status(text: str) -> GithubAuthResult:
    authenticated = "Logged in to" in text and "not logged" not in text.lower()
    match = _GH_ACCOUNT_RE.search(text)
    return GithubAuthResult(authenticated=authenticated, account=match.group(1) if match else None)


@dataclass(frozen=True)
class HfAuthResult:
    authenticated: bool
    username: str | None


def parse_hf_whoami(text: str) -> HfAuthResult:
    lowered = text.lower()
    if "not logged in" in lowered or "error" in lowered:
        return HfAuthResult(authenticated=False, username=None)
    match = _HF_WHOAMI_RE.search(text.strip())
    username = match.group(1) if match else None
    return HfAuthResult(authenticated=bool(username), username=username)


@dataclass(frozen=True)
class KaggleAuthResult:
    authenticated: bool


def parse_kaggle_auth_probe(text: str) -> KaggleAuthResult:
    """Interpret the output of a harmless authenticated call (e.g. `kaggle config view`)."""
    lowered = text.lower()
    if "authentication required" in lowered or "401" in lowered or "unauthorized" in lowered:
        return KaggleAuthResult(authenticated=False)
    return KaggleAuthResult(authenticated=True)


def platform_status(cli_installed: bool, authenticated: bool | None) -> str:
    """Fold (cli_installed, authenticated) into one of the five canonical status strings."""
    if not cli_installed:
        return NOT_CONFIGURED
    if authenticated is None:
        return NOT_EXECUTED
    return READY if authenticated else BLOCKED
