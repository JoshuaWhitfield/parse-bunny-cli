from cryptography.fernet import Fernet
from datetime import datetime
from pathlib import Path
import json
import pkgutil

CONFIG_PATH = Path("setup.enc")
KEY = b" dEC9MdSpRwrPN7R9u2BNZc8DMK3SkRASll53irOezHM="  # Paste your latest key

def load_config():
    raw = pkgutil.get_data("commands", "config.json")
    return json.loads(raw.decode("utf-8"))

def check_expiry(config):
    expiry_str = config.get("expiry")
    if not expiry_str:
        return False
    expiry = datetime.fromisoformat(expiry_str)
    return datetime.now() > expiry
