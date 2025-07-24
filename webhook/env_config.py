# webhook/env_config.py
import os

def use_json_metadata() -> bool:
    return os.getenv("TWSE_USE_JSON", "true").lower() == "true"
