#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syntax.lexer import Lexer
from commands.command import command

from syntax.lexer import Lexer 
from syntax.parser import Parser 
from syntax.interpreter import Interpreter
from syntax.prompt import Prompt 
from syntax.interface import interface

lexer = Lexer()
parser = Parser()
interp = Interpreter()
prompt = Prompt()


while interface.process_is_running():
    inputs = prompt.get_input().split(";")

    for input in inputs:
        
        lexer.set_input(lexer.reset_output() + list(input)) # reassign token and flush output token array
        lexer.Tokenize()
        
        parser.set_input(parser.reset_output() + lexer.get_output())
        parser.parse()

        interp.set_input(interp.reset_input() + parser.get_output())
        interp.Execute()
    

    


