#!/usr/bin/env python3
import sys
import time
import os
from pathlib import Path
from datetime import datetime
from secure_setup import load_encrypted_config

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

def show_logo():
    frames = [
        " " * 20 + "      (\\_/)\n" + " " * 20 + "      ( •_•)\n" + " " * 20 + "     / >🥕   \n",
        " " * 18 + "      (\\_/)\n" + " " * 18 + "      ( •_•)\n" + " " * 18 + "     / > 🥕  \n",
        " " * 16 + "      (\\_/)\n" + " " * 16 + "      ( •_•)\n" + " " * 16 + "     / > >🥕 \n",
        " " * 14 + "      (\\_/)\n" + " " * 14 + "      ( •_•)\n" + " " * 14 + "     / > > 🥕\n",
        " " * 12 + "      (\\_/)\n" + " " * 12 + "      ( •_•)\n" + " " * 12 + "     / > > \\🥕\n",
        " " * 10 + "      (\\_/)\n" + " " * 10 + "      ( •_•)\n" + " " * 10 + "     / > > \\ 🥕\n",
        " " * 8 + "      (\\_/)\n" + " " * 8 + "      ( •_•)\n" + " " * 8 + "     / > > \\  🥕\n",
        " " * 6 + "      (\\_/)\n" + " " * 6 + "      ( •_•)\n" + " " * 6 + "     / > > \\   🥕\n",
        " " * 4 + "      (\\_/)\n" + " " * 4 + "      ( •_•)\n" + " " * 4 + "     / > > \\    🥕\n",
    ]
    for _ in range(3):
        for frame in frames:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" * 5 + frame)
            time.sleep(0.15)
    print()  # space before prompt

# ===========================
# Expiry Check
# ===========================
try:
    config = load_encrypted_config()

    expiry_str = config.get("expiry")
    if not expiry_str:
        raise ValueError("Missing or empty 'expiry' field")

    expiry = datetime.fromisoformat(expiry_str).date()
    if datetime.today().date() > expiry:
        print()
        print("❌ CLI expired. Reach out to Joshua Whitfield at +1(602)-632-5714 to extend your subscription.")
        print()
        sys.exit(1)

except Exception as e:
    print(f"[config][x]: Error parsing expiry date → {e}")
    sys.exit(1)

# ===========================
# Optional Logo
# ===========================
if "-logo" in sys.argv:
    show_logo()
    sys.argv.remove("-logo")

# ===========================
# creation of .env variables
# ===========================

def ensure_env_file():
    env_path = Path("C:/parse-bunny/dashboard/.env")
    if not env_path.exists():
        print("[pbc][notif]: creating .env file. please populate it with the appropriate values.")
        env_content = """# Parse Bunny CLI Environment Variables

# Gmail credentials (for `get` command)
# for instructions, see https://myaccount.google.com/apppasswords
GGL_USER=example_user@gmail.com
GGL_PASS=xxxx xxxx xxxx xxxx

# DeepSeek API key (for AI functionality)
# while the environment variable says OpenAI, you 
# will still visit this url for an API key:
# https://platform.deepseek.com/api_keys

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(env_content, encoding="utf-8")
        print(f"[config][✓]: .env file created at {env_path}")

# ===========================
# Load environment variables from .env file
# ===========================
dotenv_path = Path("C:/parse-bunny/dashboard/.env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# ===========================
# CLI Runtime Loop
# ===========================
def main_loop():
    while interface.process_is_running():
        try:
            inputs = prompt.get_input().split(";")
        except Exception as e:
            break

        for input in inputs:
            lexer.set_input(lexer.reset_output() + list(input))
            lexer.Tokenize()
            parser.set_input(parser.reset_output() + lexer.get_output())
            parser.parse()
            interp.set_input(interp.reset_input() + parser.get_output())
            interp.Execute()


if __name__ == "__main__":
    ensure_env_file()
    main_loop()
