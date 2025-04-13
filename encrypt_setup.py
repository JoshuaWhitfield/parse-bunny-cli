# encrypt_setup.py
from cryptography.fernet import Fernet
import json

# 🔐 Generate and print the key
key = Fernet.generate_key()
print("Encryption complete. Store this key:", key.decode())

fernet = Fernet(key)

with open("setup.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

encrypted = fernet.encrypt(json.dumps(raw).encode())
with open("setup.enc", "wb") as f:
    f.write(encrypted)
