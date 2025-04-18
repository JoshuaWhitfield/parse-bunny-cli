import json
import hashlib
import requests
from pathlib import Path
from cryptography.fernet import Fernet
from datetime import datetime
import sys
import base64
from datetime import datetime, timezone

SETUP_JSON_PATH = Path("C:/parse-bunny/dashboard/setup.json")
SETUP_ENC_PATH = Path("C:/parse-bunny/dashboard/setup.enc")
SERVER_ORG_LOOKUP_URL = "http://localhost:8000/api/org/lookup"
SERVER_ADD_USER_URL = "http://localhost:8000/api/org/add_user"
SERVER_KEY_URL = "http://localhost:8000/api/org/update-key"
SERVER_LOOKUP_URL = "http://localhost:8000/api/org/lookup-key"

def generate_keys():
    full_key = Fernet.generate_key()
    short_key = full_key[:16].decode()
    long_key = full_key[16:].decode()
    return short_key, long_key, full_key

def encrypt_full_setup_blob(setup_obj, full_key):
    fernet = Fernet(full_key)
    print("encrypting full setup blob")
    return fernet.encrypt(json.dumps(setup_obj).encode())

def write_setup_enc(encrypted_blob):
    print("writing setp.enc")
    SETUP_ENC_PATH.write_bytes(encrypted_blob)

def write_setup_json(setup_obj):
    print("writing setup.json")
    SETUP_JSON_PATH.write_text(json.dumps(setup_obj, indent=2))

def register_user_if_not_exists(username, password, organization):
    try:
        print("checking for existing organization and user")
        res = requests.get(SERVER_ORG_LOOKUP_URL, params={
            "username": username,
            "organization": organization
        }, timeout=5)

        if res.status_code == 404:
            print("[setup][x] Organization not found.")
            print("Please visit the dashboard to register your organization:")
            print("→ https://www.parsebunnycli.com/dashboard → Organizations tab")
            sys.exit(1)

        data = res.json()
        if data.get("user_exists"):
            print("[setup][x] Username already exists. Please restart with a different username.")
            sys.exit(1)

        print("organization found, user not found. creating new user...")
        res_create = requests.post(
            SERVER_ADD_USER_URL,
            json={
                "organization_name": organization,
                "username": username,
                "password": password
            },
            timeout=5
        )

        if res_create.status_code != 200:
            print(f"[setup][!] Unexpected response: {res_create.status_code} → {res_create.text}")
            sys.exit(1)

    except Exception as e:
        print(f"[setup][x] Failed to contact signup: {e}")
        sys.exit(1)

def register_short_key(user_key, short_key):
    payload = {
        "user_key": user_key,
        "fernet_short_key": short_key
    }
    try:
        print("registering short key")
        res = requests.patch(SERVER_KEY_URL, json=payload, timeout=5)
        if res.status_code == 200:
            print("[setup][✓] Short key registered to server.")
        else:
            print(f"[setup][x] Server error: {res.status_code} → {res.text}")
    except Exception as e:
        print(f"[setup][x] Failed to contact server: {e}")

def create_secure_setup():
    print("[setup][~] No config found — running secure setup...\n")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    organization = input("Organization: ").strip()

    short_key, long_key, full_key = generate_keys()
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    user_key = hashlib.md5(username.encode()).hexdigest()
    db_lookup_hash = hashlib.md5((username + organization).encode()).hexdigest()

    setup_obj = {
        "profile_hash": {
            "username": username,
            "password": password_md5,
            "user_key": user_key,
            "fernet_long_key": long_key,
            "db_lookup_hash": db_lookup_hash
        },
        "organization": organization,
        "features": ["label", "extract", "highlight", "reset", "get"],
        "expiry": "2025-06-30"
    }

    encrypted_blob = encrypt_full_setup_blob(setup_obj, full_key)

    register_user_if_not_exists(username, password, organization)
    write_setup_enc(encrypted_blob)
    write_setup_json(setup_obj)
    register_short_key(user_key, short_key)

    print("\n[setup][✓] setup.json and setup.enc created securely.")

def load_encrypted_config():
    setup_json = json.loads(SETUP_JSON_PATH.read_text())
    username = setup_json["profile_hash"]["username"]
    organization = setup_json.get("organization")

    print(f"[auth][~] Looking up short key for {username} in {organization}...")
    
    res = requests.get(
        SERVER_LOOKUP_URL,
        params={"username": username, "organization": organization},
        timeout=5
    )
    if res.status_code != 200:
        raise Exception("Could not fetch short key")

    short_key = res.json().get("fernet_short_key")
    if not short_key:
        raise Exception("Short key missing in server response")

    long_key = setup_json["profile_hash"]["fernet_long_key"]

    try:
        raw_short = base64.urlsafe_b64decode(short_key + '=' * (-len(short_key) % 4))
        raw_long = base64.urlsafe_b64decode(long_key + '=' * (-len(long_key) % 4))
    except Exception as e:
        raise Exception(f"[auth][x] Failed to base64-decode keys: {e}")

    combined_raw = raw_short + raw_long
    if len(combined_raw) != 32:
        raise Exception(f"[auth][x] Combined key length invalid: {len(combined_raw)} bytes")

    full_key = base64.urlsafe_b64encode(combined_raw)

    fernet = Fernet(full_key)
    encrypted_blob = SETUP_ENC_PATH.read_bytes()
    decrypted = fernet.decrypt(encrypted_blob).decode()
    config = json.loads(decrypted)

    # Expiry check
    expiry_str = config.get("expiry")
    if expiry_str:
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry_date:
            raise Exception("[auth][x] License has expired. Please renew to continue using this tool.")

    if not all(k in config.get("profile_hash", {}) for k in ("username", "user_key", "fernet_long_key", "password", "db_lookup_hash")):
        raise Exception("[auth][x] Decrypted blob missing required profile_hash fields")

    if "organization" not in config:
        raise Exception("[auth][x] Decrypted blob missing organization field")

    print("[auth] Signing in...")
    return config
