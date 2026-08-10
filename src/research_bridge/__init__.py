"""Multi-platform research bridge (GitHub / Colab / Hugging Face / Kaggle / Drive).

Pure, testable logic only — nothing here calls a live CLI or network endpoint. GitHub remains
the canonical source of truth (git SHA, dataset SHA, config SHA, experiment ID never get
overridden by anything computed on another platform). See docs/RESEARCH_PLATFORM_BRIDGE.md.
"""

from .config import BridgeConfigError, DEFAULT_CONFIG_PATH, get_value, load_config

__all__ = ["BridgeConfigError", "DEFAULT_CONFIG_PATH", "get_value", "load_config"]
