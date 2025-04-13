#!/usr/bin/env python3
import sys
import time
import os
from pathlib import Path
import requests

from syntax.lexer import Lexer
from commands.command import command
from syntax.parser import Parser
from syntax.interpreter import Interpreter
from syntax.prompt import Prompt
from syntax.interface import interface
from secure_setup import load_encrypted_config, check_expiry
from commands.config import load_config, check_expiry

lexer = Lexer()
parser = Parser()
interp = Interpreter()
prompt = Prompt()

def show_logo():
    frames = [
        " " * 20 + "      (\\_/)\n" +
        " " * 20 + "      ( •_•)\n" +
        " " * 20 + "     / >🥕   \n",

        " " * 18 + "      (\\_/)\n" +
        " " * 18 + "      ( •_•)\n" +
        " " * 18 + "     / > 🥕  \n",

        " " * 16 + "      (\\_/)\n" +
        " " * 16 + "      ( •_•)\n" +
        " " * 16 + "     / > >🥕 \n",

        " " * 14 + "      (\\_/)\n" +
        " " * 14 + "      ( •_•)\n" +
        " " * 14 + "     / > > 🥕\n",

        " " * 12 + "      (\'_/)\n" +
        " " * 12 + "      ( •_•)\n" +
        " " * 12 + "     / > > \\🥕\n",

        " " * 10 + "      (\\_/)\n" +
        " " * 10 + "      ( •_•)\n" +
        " " * 10 + "     / > > \\ 🥕\n",

        " " * 8 + "      (\\_/)\n" +
        " " * 8 + "      ( •_•)\n" +
        " " * 8 + "     / > > \\  🥕\n",

        " " * 6 + "      (\\_/)\n" +
        " " * 6 + "      ( •_•)\n" +
        " " * 6 + "     / > > \\   🥕\n",

        " " * 4 + "      (\\_/)\n" +
        " " * 4 + "      ( •_•)\n" +
        " " * 4 + "     / > > \\    🥕\n",
    ]

    count = 0
    while count < 3:
        count += 1
        for frame in frames:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" * 5 + frame)
            time.sleep(0.15)
    print()  # crucial do not remove

# If the logo flag is passed, display logo then remove it from args

from commands.config import load_config
from datetime import datetime

config = load_config()
if datetime.today().date() > datetime.fromisoformat(config["expiry"]).date():
    print()
    print("❌ CLI expired. reach out to Joshua Whitfield at +1(602)-632-5714 to extend your subscription.")
    print()
    exit(1)

# continue CLI startup here...

if "-logo" in sys.argv:
    show_logo()
    sys.argv.remove("-logo")

# CLI loop
while interface.process_is_running():
    inputs = prompt.get_input().split(";")

    for input in inputs:
        lexer.set_input(lexer.reset_output() + list(input))  # reassign token and flush output token array
        lexer.Tokenize()

        parser.set_input(parser.reset_output() + lexer.get_output())
        parser.parse()

        interp.set_input(interp.reset_input() + parser.get_output())
        interp.Execute()
