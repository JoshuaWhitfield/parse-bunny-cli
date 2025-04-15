from datetime import datetime
import json
import os
import sys
import pkgutil
from pathlib import Path

def get_base_path():
    """Resolves the base directory, works in development and PyInstaller bundle."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)  # PyInstaller temp directory
    return Path(__file__).resolve().parent.parent  # project root in dev

def load_config():
    # Check if we're running in a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print("[config][i]: Running in PyInstaller bundle")
        # We're running in a PyInstaller bundle
        try:
            config_path = os.path.join(sys._MEIPASS, "commands", "config.json")
            print(f"[config][i]: Looking for config at {config_path}")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[config][x]: Error loading config in PyInstaller: {e}")
    else:
        # Normal Python execution - try pkgutil
        try:
            data = pkgutil.get_data("commands", "config.json")
            if data:
                return json.loads(data.decode("utf-8"))
        except Exception as e:
            print(f"[config][x]: Error loading config.json via pkgutil: {e}")
    
    # Default configuration as last resort
    print("[config][!]: Using default configuration")
    return {
        "API_KEY": "AIzaSyBksscECxkxH6tAmt-ClUKjU5p8AdcrkMM",
        "CSE_ID": "453cd0a59cf514667",
        "expiry": "2025-05-31"
    }

def check_expiry(config):
    """Check if the configuration has expired."""
    try:
        expiry_str = config.get("expiry")
        if not expiry_str:
            print("[config][!]: No expiry date found, using default")
            return False
            
        expiry = datetime.fromisoformat(expiry_str)
        is_expired = datetime.now() > expiry
        if is_expired:
            print("[config][x]: Configuration has expired")
        return is_expired
    except Exception as e:
        print(f"[config][!]: Error checking expiry: {str(e)}")
        return False  # Default to not expired