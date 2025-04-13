from cryptography.fernet import Fernet
import json
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path("setup.enc")
KEY = b"b8p33_zr4zGf8DKV4c4bNFpe_xmNlc0dNfLmy7JKY8c="  # Paste your latest key

def load_config():
    fernet = Fernet(KEY)
    decrypted = fernet.decrypt(CONFIG_PATH.read_bytes())
    return json.loads(decrypted.decode("utf-8"))

def check_expiry(config):
    expiry_str = config.get("expiry")
    if not expiry_str:
        return False
    expiry = datetime.fromisoformat(expiry_str)
    return datetime.now() > expiry
