#!/usr/bin/env python3
import sys
import time
import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from syntax.lexer import Lexer
from syntax.parser import Parser
from syntax.interpreter import Interpreter
from syntax.prompt import Prompt
from syntax.interface import interface
from dotenv import load_dotenv

lexer = Lexer()
parser = Parser()
interp = Interpreter()
prompt = Prompt()

SETUP_JSON_PATH = Path("C:/parse-bunny/dashboard/setup.json")
SETUP_HASH_PATH = Path("C:/parse-bunny/dashboard/setup.enc")
SERVER_URL = "http://localhost:8000/api"

# ===========================
# Show Logo
# ===========================
def show_logo():
    frames = [
        " " * 20 + "      (\\_/)" + " " * 20 + "      ( •_•)" + " " * 20 + "     / >🥕   ",        " " * 18 + "      (\\_/)" + " " * 18 + "      ( •_•)" + " " * 18 + "     / > 🥕  ",        " " * 16 + "      (\\_/)" + " " * 16 + "      ( •_•)" + " " * 16 + "     / > >🥕 ",        " " * 14 + "      (\\_/)" + " " * 14 + "      ( •_•)" + " " * 14 + "     / > > 🥕",        " " * 12 + "      (\\_/)" + " " * 12 + "      ( •_•)" + " " * 12 + "     / > > \\🥕",        " " * 10 + "      (\\_/)" + " " * 10 + "      ( •_•)" + " " * 10 + "     / > > \\ 🥕",        " " * 8 + "      (\\_/)" + " " * 8 + "      ( •_•)" + " " * 8 + "     / > > \\  🥕",        " " * 6 + "      (\\_/)" + " " * 6 + "      ( •_•)" + " " * 6 + "     / > > \\   🥕",        " " * 4 + "      (\\_/)" + " " * 4 + "      ( •_•)" + " " * 4 + "     / > > \\    🥕",
    ]
    for _ in range(3):
        for frame in frames:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" * 5 + frame)
            time.sleep(0.15)
    print()

# ===========================
# .env setup
# ===========================
def ensure_env_file():
    env_path = Path("C:/parse-bunny/dashboard/.env")
    if not env_path.exists():
        print("[pbc][notif]: creating .env file. please populate it with the appropriate values.")
        env_content = """# Parse Bunny CLI Environment Variables
            GGL_USER=example_user@gmail.com
            GGL_PASS=xxxx xxxx xxxx xxxx
            OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            """
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(env_content, encoding="utf-8")
        print(f"[config][✓]: .env file created at {env_path}")

dotenv_path = Path("C:/parse-bunny/dashboard/.env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# ===========================
# Main loop
# ===========================
def main_loop():
    while interface.process_is_running():
        try:
            inputs = prompt.get_input().split(";")
        except Exception:
            break

        for input in inputs:
            lexer.set_input(lexer.reset_output() + list(input))
            lexer.Tokenize()
            parser.set_input(parser.reset_output() + lexer.get_output())
            parser.parse()
            interp.set_input(interp.reset_input() + parser.get_output())
            interp.Execute()

# ===========================
# Setup handling (MD5 hash instead of Fernet encryption)
# ===========================
def generate_md5_from_json(setup):
    serialized = json.dumps(setup, sort_keys=True)
    return hashlib.md5(serialized.encode()).hexdigest()

def prompt_for_user():
    username = input("Username: ").strip()
    password = input("Password: ").strip()  # Stored in profile for lookup only
    return {"username": username, "password": password}

def create_setup():
    profile = prompt_for_user()
    setup = {
        "expiry": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "features": ["label", "extract", "redact", "highlight", "search", "reset", "get"],
        "profile_hash": profile
    }
    with open(SETUP_JSON_PATH, "w") as f:
        json.dump(setup, f, indent=2)
    md5_hash = generate_md5_from_json(setup)
    with open(SETUP_HASH_PATH, "w") as f:
        f.write(md5_hash)

    try:
        requests.post(f"{SERVER_URL}/register", json={"username": profile['username'], "md5": md5_hash})
        print("[setup][✓] Registered setup with server.")
    except Exception as e:
        print(f"[setup][x] Failed to send to server: {e}")

    print("[setup][✓] setup.json created and hashed to setup.enc")

def validate_and_run():
    if not SETUP_HASH_PATH.exists() or not SETUP_JSON_PATH.exists():
        print("[setup] No config found — running first-time setup.")
        create_setup()
    else:
        print("[setup][✓] setup.json and setup.enc found. Continuing...")

# ===========================
# Boot
# ===========================
if __name__ == "__main__":
    if "-logo" in sys.argv:
        show_logo()
        sys.argv.remove("-logo")

    validate_and_run()
    main_loop()