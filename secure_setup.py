# secure_config.py
import json
from datetime import datetime
from cryptography.fernet import Fernet

FERNET_KEY = b"qaKU1pv5J1uvJu_yqDmMqr5cEOWclvkX7JBxREBCVT8="

def load_encrypted_config(path="setup.enc"):
    with open(path, "rb") as f:
        encrypted_data = f.read()

    fernet = Fernet(FERNET_KEY)
    decrypted_data = fernet.decrypt(encrypted_data)
    config = json.loads(decrypted_data.decode())
    return config

def check_expiry(config):
    expiry = config.get("expiry")
    if not expiry:
        print("[config][x]: Expiry date missing")
        exit(1)

    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
    if datetime.now() > expiry_date:
        print("[license][x]: License expired. CLI will now exit.")
        exit(1)
