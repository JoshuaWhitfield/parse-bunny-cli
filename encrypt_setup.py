# encrypt_setup.py
from cryptography.fernet import Fernet
import json

key = b"qaKU1pv5J1uvJu_yqDmMqr5cEOWclvkX7JBxREBCVT8="
fernet = Fernet(key)

with open("setup.json", "r") as f:
    config = json.load(f)

encrypted = fernet.encrypt(json.dumps(config).encode())

with open("setup.enc", "wb") as f:
    f.write(encrypted)

print("Encrypted config with expiry:", config["expiry"])
