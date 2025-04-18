from pathlib import Path
import json
import base64
import requests
from cryptography.fernet import Fernet

# Paths
BACKUP_LOCK_PATH = Path("C:/parse-bunny/dashboard/data/memory/backups/lock/backup.lock")
BACKUP_JSON_PATH = Path("C:/parse-bunny/dashboard/data/memory/backups/backups.json")
BACKUP_ENC_PATH = Path("C:/parse-bunny/dashboard/data/memory/backups/backups.enc")

# Server URLs
SERVER_PUSH_URL = "http://localhost:8000/api/backups/push"
SERVER_PULL_URL = "http://localhost:8000/api/backups/pull"

SETUP_JSON_PATH = Path("C:/parse-bunny/dashboard/setup.json")
BACKUP_LOCK_PATH = Path("C:/parse-bunny/dashboard/data/memory/backups/lock/backup.lock")
BACKUP_ENC_JSON = Path("C:/parse-bunny/dashboard/data/memory/backups/backup.json")
BACKUP_ENC_KEY = Path("C:/parse-bunny/dashboard/data/memory/backups/backup.enc")
SERVER_BACKUP_PUSH_URL = "http://localhost:8000/api/backups/push"

def get_setup():
    return json.loads(SETUP_JSON_PATH.read_text(encoding="utf-8"))

def encrypt_and_push(path, backup_name):
    setup = get_setup()
    username = setup["profile_hash"]["username"]
    user_key = setup["profile_hash"]["user_key"]
    org = setup["organization"]

    full_key = Fernet.generate_key()
    short_key = full_key[:16]
    long_key = full_key[16:]
    fernet = Fernet(full_key)

    path = Path(path)
    if path.is_dir():
        structure = {}
        for file in path.rglob("*"):
            if file.is_file():
                content = file.read_text(encoding="utf-8")
                structure[str(file.relative_to(path))] = content
        payload = json.dumps(structure)
    else:
        payload = path.read_text(encoding="utf-8")

    encrypted_data = fernet.encrypt(payload.encode())
    BACKUP_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_LOCK_PATH.write_bytes(encrypted_data)

    BACKUP_ENC_KEY.write_text(long_key.decode())
    with open(BACKUP_ENC_JSON, "w", encoding="utf-8") as f:
        json.dump({backup_name: short_key.decode()}, f, indent=2)

    res = requests.post(SERVER_BACKUP_PUSH_URL, json={
        "organization": org,
        "cli_user_key": user_key,
        "backup_name": backup_name,
        "encrypted_data": base64.b64encode(encrypted_data).decode()
    })

    if res.status_code == 200:
        print(f"[push][✓] Backup {backup_name} pushed to server")
    else:
        print(f"[push][x] Failed to push: {res.status_code} → {res.text}")

def pull_backup(cli_key: str, organization: str, name: str) -> dict:
    """
    Pulls a Fernet-encrypted backup from the server and writes it to `backup.lock`.
    Requires local long key from `backups.enc`.
    """
    # Step 1: Retrieve encrypted backup from server
    response = requests.get(SERVER_PULL_URL, params={
        "cli_key": cli_key,
        "organization": organization,
        "backup_name": name
    })

    if response.status_code != 200:
        raise Exception(f"[pull][x] Server error: {response.status_code} → {response.text}")

    encoded_data = response.json().get("encrypted_data")
    if not encoded_data:
        raise Exception("[pull][x] No encrypted data found for requested backup")

    encrypted_data = base64.b64decode(encoded_data)

    # Step 2: Load local short and long keys
    short_key = name.encode()[:16]  # fallback dummy short key based on name
    long_key = None

    if BACKUP_ENC_PATH.exists():
        long_keys = json.loads(BACKUP_ENC_PATH.read_text())
        long_key = long_keys.get(name)

    if not long_key:
        raise Exception("[pull][x] No long key found for backup name")

    # Step 3: Combine and decrypt
    full_key_bytes = base64.urlsafe_b64encode(short_key + long_key.encode())
    fernet = Fernet(full_key_bytes)
    decrypted_data = json.loads(fernet.decrypt(encrypted_data).decode())

    # Step 4: Save encrypted copy to backup.lock
    BACKUP_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_LOCK_PATH.write_bytes(encrypted_data)

    return decrypted_data

def encrypt_backup(data: dict, short_key: str) -> bytes:
    key = base64.urlsafe_b64encode(short_key.encode() * 2)
    fernet = Fernet(key)
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_backup(encrypted_data: bytes, short_key: str) -> dict:
    key = base64.urlsafe_b64encode(short_key.encode() * 2)
    fernet = Fernet(key)
    return json.loads(fernet.decrypt(encrypted_data).decode())

def save_local_backup(name: str, encrypted_blob: bytes):
    BACKUP_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_LOCK_PATH.write_bytes(encrypted_blob)
    
    BACKUP_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    backups = {}
    if BACKUP_JSON_PATH.exists():
        backups = json.loads(BACKUP_JSON_PATH.read_text())
    backups[name] = {"path": str(BACKUP_LOCK_PATH)}
    BACKUP_JSON_PATH.write_text(json.dumps(backups, indent=2))

def load_local_backup() -> bytes:
    if BACKUP_LOCK_PATH.exists():
        return BACKUP_LOCK_PATH.read_bytes()
    return None

def save_long_key_for_backup(name: str, long_key: str):
    BACKUP_ENC_PATH.parent.mkdir(parents=True, exist_ok=True)
    keys = {}
    if BACKUP_ENC_PATH.exists():
        keys = json.loads(BACKUP_ENC_PATH.read_text())
    keys[name] = long_key
    BACKUP_ENC_PATH.write_text(json.dumps(keys, indent=2))

def get_long_key_for_backup(name: str) -> str:
    if BACKUP_ENC_PATH.exists():
        keys = json.loads(BACKUP_ENC_PATH.read_text())
        return keys.get(name)
    return None

def push_backup_to_server(cli_key: str, organization: str, name: str, encrypted_blob: bytes):
    res = requests.post(SERVER_PUSH_URL, json={
        "cli_key": cli_key,
        "organization": organization,
        "backup_name": name,
        "encrypted_data": base64.b64encode(encrypted_blob).decode()
    })
    if res.status_code != 200:
        raise Exception(f"[push][x] Server responded with error: {res.status_code} → {res.text}")
    print(f"[push][✓] Server stored backup '{name}'.")

def pull_backup_from_server(cli_key: str, organization: str, name: str) -> bytes:
    res = requests.get(SERVER_PULL_URL, params={
        "cli_key": cli_key,
        "organization": organization,
        "backup_name": name
    })
    if res.status_code != 200:
        raise Exception(f"[pull][x] Server responded with error: {res.status_code} → {res.text}")
    return base64.b64decode(res.json()["encrypted_data"])

def generate_fernet_keys():
    """Generates a Fernet key and splits it into short and long parts."""
    full_key = Fernet.generate_key()
    short_key = full_key[:16].decode()
    long_key = full_key[16:].decode()
    return short_key, long_key, full_key

def encrypt_file_content(file_path, full_key):
    """Encrypts the contents of a file using the given Fernet key."""
    fernet = Fernet(full_key)
    content = Path(file_path).read_text(encoding='utf-8')
    encrypted = fernet.encrypt(content.encode())
    return encrypted.decode()

def recursively_encrypt_dir(dir_path, full_key):
    """Recursively encrypt all file contents in a directory."""
    encrypted_files = {}
    for path in Path(dir_path).rglob('*'):
        if path.is_file():
            relative_path = path.relative_to(dir_path).as_posix()
            encrypted_files[relative_path] = encrypt_file_content(path, full_key)
    return encrypted_files
