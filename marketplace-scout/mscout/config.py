from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config(path: str | os.PathLike | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else DEFAULT_CONFIG
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    for key in ("profile_dir", "cache_db", "gcp_service_account"):
        cfg["paths"][key] = str(Path(cfg["paths"][key]).expanduser())
    Path(cfg["paths"]["profile_dir"]).parent.mkdir(parents=True, exist_ok=True)
    return cfg
