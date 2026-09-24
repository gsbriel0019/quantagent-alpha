import os
import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
SETTINGS_PATH = CONFIG_DIR / "settings.yaml"

def load_settings():
    if not SETTINGS_PATH.exists():
        return {}
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

SETTINGS = load_settings()
