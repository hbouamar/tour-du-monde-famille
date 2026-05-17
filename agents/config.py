import json
import os
from pathlib import Path


def load_config():
    """Charge config.json (Pi) si présent, sinon utilise les variables d'env (GitHub Actions)."""
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        return
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)
    for key, value in cfg.items():
        if key not in os.environ:
            os.environ[key] = str(value)
