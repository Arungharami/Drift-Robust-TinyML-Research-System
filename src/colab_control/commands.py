"""Colab CLI command construction, isolated so it is unit-testable (Mission 40).

SYNTAX_VERIFIED is False until `colab --help` / `colab <subcmd> --help` has actually been
inspected inside WSL2 against the installed google-colab-cli version (Missions 4, 9, 10). The
shapes below mirror this project's documented conceptual interface; scripts/colab/*.sh call
`colab` directly rather than through this module today, but keep the argv shapes identical so
this module stays the single reference for "what command did we intend to run" in tests and
docs. Re-verify and update both places together once the real CLI is installed.
"""
from __future__ import annotations

SYNTAX_VERIFIED = False


def colab_new_session(session: str, gpu: str | None = None, auth: str = "oauth2") -> list[str]:
    cmd = ["colab", f"--auth={auth}", "new", "-s", session]
    if gpu:
        cmd += ["--gpu", gpu]
    return cmd


def colab_status(session: str, auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "status", "-s", session]


def colab_sessions(auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "sessions"]


def colab_stop(session: str, auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "stop", "-s", session]


def colab_upload(session: str, local_path: str, remote_path: str, auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "upload", "-s", session, local_path, remote_path]


def colab_download(session: str, remote_path: str, local_path: str, auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "download", "-s", session, remote_path, local_path]


def colab_log(session: str, fmt: str = "jsonl", auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "log", "-s", session, "--format", fmt]


def colab_drivemount(session: str, auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "drivemount", "-s", session]


def colab_run(script_path: str, auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "run", script_path]


def colab_exec(session: str, command: list[str], auth: str = "oauth2") -> list[str]:
    return ["colab", f"--auth={auth}", "exec", "-s", session, "--", *command]
