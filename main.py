from syntax.lexer import Lexer 
from syntax.parser import Parser 
from syntax.interpreter import Interpreter
from syntax.prompt import Prompt 

lexer = Lexer()
parser = Parser()
interp = Interpreter()
prompt = Prompt()

while True:
    inputs = prompt.get_input().split(";")

    for input in inputs:
        
        lexer.set_input(lexer.reset_output() + list(input)) # reassign token and flush output token array
        lexer.Tokenize()
        
        parser.set_input(parser.reset_output() + lexer.get_output())
        parser.parse()

        interp.set_input(interp.reset_input() + parser.get_output())
        interp.Execute()
    

    


