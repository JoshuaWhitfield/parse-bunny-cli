# config.py - place this in the commands directory
from cryptography.fernet import Fernet
from datetime import datetime
import json
import os
import sys
from pathlib import Path

def get_base_path():
    """Get the base path for resources, works in both development and PyInstaller executable"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in development mode
        return Path(__file__).parent.parent

def load_encrypted_config():
    try:
        # Determine base path
        base_path = get_base_path()
        key_path = base_path / "key.bin"
        setup_enc_path = base_path / "setup.enc"
        
        print(f"[config][?] Looking for key at: {key_path}")
        print(f"[config][?] Looking for encrypted config at: {setup_enc_path}")
        
        # Check if key exists, generate if not
        if not key_path.exists():
            print(f"[config][!] Key file not found, generating new key")
            key = Fernet.generate_key()
            # In development mode, we can create the key file
            if not getattr(sys, 'frozen', False):
                try:
                    with open(key_path, "wb") as f:
                        f.write(key)
                    print(f"[config][✓] New key saved to {key_path}")
                except Exception as e:
                    print(f"[config][!] Could not save key: {e}")
            else:
                print(f"[config][!] Running in bundle mode, key will not be saved")
        else:
            # Load existing key
            key = key_path.read_bytes()
            print(f"[config][✓] Using existing key from {key_path}")
            
        fernet = Fernet(key)

        # Decrypt the encrypted setup if it exists
        if not setup_enc_path.exists():
            print(f"[config][x] Encrypted config not found at {setup_enc_path}")
            # Generate default config
            default_config = {
                "API_KEY": "",  # Empty values by default
                "CSE_ID": "",
                "expiry": (datetime.now().replace(microsecond=0) + 
                          datetime.timedelta(days=30)).isoformat()
            }
            
            # In development mode, encrypt and save the default config
            if not getattr(sys, 'frozen', False):
                try:
                    encrypted = fernet.encrypt(json.dumps(default_config).encode())
                    with open(setup_enc_path, "wb") as f:
                        f.write(encrypted)
                    print(f"[config][✓] Generated default encrypted config at {setup_enc_path}")
                except Exception as e:
                    print(f"[config][x]: Failed to load encrypted config → {repr(e)}")

            
            return default_config
            
        # Decrypt existing encrypted setup
        decrypted = fernet.decrypt(setup_enc_path.read_bytes())
        setup_config = json.loads(decrypted.decode("utf-8"))
        
        print("[config][✓] Successfully loaded encrypted config")
        return setup_config
    except Exception as e:
        print(f"[config][x]: Failed to load encrypted config → {e}")
        # Return empty default values as fallback
        return {
            "API_KEY": "",
            "CSE_ID": "",
            "expiry": datetime.now().replace(microsecond=0).isoformat()
        }

def get_key():
    """Get the encryption key from the key file"""
    try:
        key_path = get_base_path() / "key.bin"
        print(f"[config][?] Looking for key at: {key_path}")
        
        if key_path.exists():
            with open(key_path, "rb") as f:
                key = f.read()
            print("[config][✓] Successfully loaded encryption key")
            return key
        else:
            print("[config][x] Key file not found")
            return None
    except Exception as e:
        print(f"[config][x] Error loading key: {str(e)}")
        return None

def load_config():
    """Load configuration from encrypted file or fallback to defaults"""
    try:
        # Get the encryption key
        key = get_key()
        if not key:
            raise ValueError("Encryption key not found")
        
        # Try the encrypted file
        base_path = get_base_path() if getattr(sys, 'frozen', False) else Path(__file__).parent
        config_path = base_path / "setup.enc"
        
        # Debug info
        print(f"[config][?] Looking for encrypted config at: {config_path}")
        
        if config_path.exists():
            fernet = Fernet(key)
            encrypted_data = config_path.read_bytes()
            decrypted = fernet.decrypt(encrypted_data)
            config = json.loads(decrypted.decode())
            print("[config][✓] Successfully loaded encrypted config")
            return config
        else:
            print("[config][!] Encrypted config not found, using default values")
            
        # Fallback to default values
        return {
            "API_KEY": "AIzaSyBksscECxkxH6tAmt-ClUKjU5p8AdcrkMM", 
            "CSE_ID": "453cd0a59cf514667", 
            "expiry": "2025-05-31"
        }
    except Exception as e:
        print(f"[config][x] Error loading config: {str(e)}")
        # Return default values
        return {
            "API_KEY": "AIzaSyBksscECxkxH6tAmt-ClUKjU5p8AdcrkMM", 
            "CSE_ID": "453cd0a59cf514667", 
            "expiry": "2025-05-31"
        }

def check_expiry(config):
    """Check if the configuration has expired"""
    try:
        expiry_str = config.get("expiry")
        if not expiry_str:
            print("[config][!] No expiry date found, using default")
            return False
            
        expiry = datetime.fromisoformat(expiry_str)
        is_expired = datetime.now() > expiry
        if is_expired:
            print("[config][x] Configuration has expired")
        return is_expired
    except Exception as e:
        print(f"[config][!] Error checking expiry: {str(e)}")
        return False  # Default to not expired