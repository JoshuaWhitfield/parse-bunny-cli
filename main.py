#!/usr/bin/env python3
import sys
import time
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from syntax.lexer import Lexer
from syntax.parser import Parser
from syntax.interpreter import Interpreter
from syntax.prompt import Prompt
from syntax.interface import interface
from commands.secure_setup import load_encrypted_config, create_secure_setup
from commands.config import check_expiry

# Core interpreters
lexer = Lexer()
parser = Parser()
interp = Interpreter()
prompt = Prompt()

# Paths
SETUP_JSON_PATH = Path("C:/parse-bunny/dashboard/setup.json")
SETUP_ENC_PATH = Path("C:/parse-bunny/dashboard/setup.enc")
SERVER_URL = "http://localhost:8000/api"
dotenv_path = Path("C:/parse-bunny/dashboard/.env")

# ===========================
# Logo Animation
# ===========================
def show_logo():
    frames = [
        " " * 20 + "      (\\_/)" + " " * 20 + "      ( •_•)" + " " * 20 + "     / >🥕   ",
        " " * 4 + "      (\\_/)" + " " * 4 + "      ( •_•)" + " " * 4 + "     / > > \\    🥕"
    ]
    for _ in range(3):
        for frame in frames:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" * 5 + frame)
            time.sleep(0.15)
    print()

# ===========================
# .env File Setup
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
        print(f"[config][✓] .env file created at {env_path}")

if dotenv_path.exists():
    load_dotenv(dotenv_path)

# ===========================
# Main Loop
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
# First-Time Setup Check
# ===========================
def validate_and_run():
    if not SETUP_JSON_PATH.exists() or not SETUP_ENC_PATH.exists():
        print("[setup][~] No config found — running secure setup...")
        create_secure_setup()
    else:
        print("[setup][✓] setup.json and setup.enc found. Continuing...")

# ===========================
# Set Password If Missing
# ===========================
def set_password_if_none():
    try:
        setup = load_encrypted_config()
        username = setup["profile_hash"]["username"]
        password = setup["profile_hash"]["password"]
    except Exception as e:
        print(f"[auth][x] Could not load config: {e}")
        return

    organization_name = input("Enter your organization name: ").strip()

    payload = {
        "username": username,
        "organization_name": organization_name,
        "new_password": password
    }

    try:
        res = requests.patch(f"{SERVER_URL}/org/update-password", json=payload)
        if res.status_code == 200:
            print("[auth][✓] Password successfully set on server.")
        elif res.status_code == 404:
            print("[auth] Proceeding smart login...") # password was already set or user not found. user is hardcoded so is always found unless deleted from server.
        else:
            print(f"[auth][x] Server responded with error: {res.text}")
    except Exception as e:
        print(f"[auth][x] Failed to update password: {e}")

# ===========================
# Boot
# ===========================
if __name__ == "__main__":
    if "-logo" in sys.argv:
        show_logo()
        sys.argv.remove("-logo")

    ensure_env_file()
    validate_and_run()
    set_password_if_none()
    main_loop()
