from cryptography.fernet import Fernet
from datetime import datetime
import json
from pathlib import Path

KEY = b"qaKU1pv5J1uvJu_yqDmMqr5cEOWclvkX7JBxREBCVT8="

def load_encrypted_config():
    try:
        CONFIG_PATH = Path(__file__).parent / "setup.enc"
        fernet = Fernet(KEY)
        decrypted = fernet.decrypt(CONFIG_PATH.read_bytes())
        config = json.loads(decrypted.decode())
        return config
    except Exception as e:
        print("[config][x]: Failed to load encrypted config →", repr(e))  # Print full exception
        return {}

def check_expiry(config):
    try:
        expiry = config.get("expiry", "")
        if not expiry:
            raise ValueError("Missing or empty 'expiry' field")
        expiry_date = datetime.fromisoformat(expiry).date()
        return datetime.today().date() > expiry_date
    except Exception as e:
        print("[config][x]: Error parsing expiry date →", repr(e))
        return True
