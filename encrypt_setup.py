# encrypt_setup.py
from cryptography.fernet import Fernet
import json
from pathlib import Path

# Paths
config_path = Path("commands/config.json")
enc_path = Path("setup.enc")
key_path = Path("key.bin")

# Load original config
with open(config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)

# Encrypt
key = Fernet.generate_key()
fernet = Fernet(key)
encrypted_data = fernet.encrypt(json.dumps(config_data).encode("utf-8"))

# Save encrypted config
with open(enc_path, "wb") as enc_file:
    enc_file.write(encrypted_data)

# Save key
with open(key_path, "wb") as key_file:
    key_file.write(key)

print("[encrypt][✓] Encrypted setup written to setup.enc")
print("[encrypt][✓] Key written to key.bin")