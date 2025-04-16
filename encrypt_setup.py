# encrypt_setup.py
import json
from cryptography.fernet import Fernet

def encrypt_setup_json():
    with open("setup.json", "r") as f:
        data = f.read()

    # Generate Fernet key (long key = full 44 bytes)
    key = Fernet.generate_key()
    fernet = Fernet(key)

    encrypted = fernet.encrypt(data.encode())

    # Write encrypted output
    with open("setup.enc", "wb") as ef:
        ef.write(encrypted)

    print("[✓] Encrypted setup.json → setup.enc")
    print("[✓] Fernet key (long):", key.decode())

    # Optionally delete plaintext
    # os.remove("setup.json")

    return key.decode()

if __name__ == "__main__":
    encrypt_setup_json()
