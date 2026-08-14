"""Environment labels for every executed run.

Absolute rule (see repo mission brief): never confuse LOCAL_WINDOWS execution with WSL
execution, real Colab CPU, real Colab GPU, or physical nRF52840 hardware. Every run manifest
must carry one of these labels, inferred by inspecting the actual runtime — never assumed from
a requested allocation (a GPU request can still land on CPU-only capacity, for example).
"""
from __future__ import annotations

ALLOWED_ENVIRONMENT_LABELS = frozenset(
    {
        "LOCAL_WINDOWS_CPU",
        "LOCAL_WINDOWS_GPU",
        "WSL_LOCAL",
        "COLAB_CPU",
        "COLAB_T4",
        "COLAB_L4",
        "COLAB_G4",
        "COLAB_A100",
        "COLAB_H100",
        "PHYSICAL_NRF52840",
    }
)


class InvalidEnvironmentLabelError(ValueError):
    pass


def validate_environment_label(label: str) -> str:
    """Return `label` unchanged if allowed, else raise InvalidEnvironmentLabelError."""
    if label not in ALLOWED_ENVIRONMENT_LABELS:
        raise InvalidEnvironmentLabelError(
            f"{label!r} is not an allowed environment label; inspect the actual runtime and "
            f"choose one of: {sorted(ALLOWED_ENVIRONMENT_LABELS)}"
        )
    return label
