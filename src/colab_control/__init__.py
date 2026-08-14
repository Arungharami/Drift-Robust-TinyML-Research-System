"""Colab CLI research control plane — pure, testable logic used by scripts/colab/*.sh.

Nothing in this package executes a real Colab session or shells out to the `colab` CLI.
It only handles: config loading/validation, environment-label enforcement, run-id/manifest
construction, workspace include/exclude resolution, CLI command-string construction, and
local-vs-Colab result comparison. That split is deliberate (Mission 40): this logic must be
unit-testable in ordinary CI without a paid/remote Colab allocation.
"""

from .config import ColabConfigError, DEFAULT_CONFIG_PATH, get_value, load_config
from .environments import ALLOWED_ENVIRONMENT_LABELS, InvalidEnvironmentLabelError, validate_environment_label

__all__ = [
    "ColabConfigError",
    "DEFAULT_CONFIG_PATH",
    "get_value",
    "load_config",
    "ALLOWED_ENVIRONMENT_LABELS",
    "InvalidEnvironmentLabelError",
    "validate_environment_label",
]
