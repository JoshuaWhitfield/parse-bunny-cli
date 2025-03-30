from syntax.lexer import Lexer 
from syntax.parser import Parser 
from syntax.interpreter import Interpreter

lexer = Lexer()
parser = Parser()
interp = Interpreter()

inputs = [
    # 'ip_address = 10.10.10.10',
    # 'hack(ip_address, 80) --flag -flag2',
    # 'pbc understand hack',
    # 'variable =',
    # 'func(',
    # 'func)',
    # 'clear'
    'data -collect -template[std] -search-engine["quantum physics", "award winning", "new discovery", "2019"]'
]

iter = 0
for input in inputs:
    iter += 1
    print("################################################################")
    print(f'iteration {iter}')
    print("input: "+ input) 
    lexer.set_input(lexer.reset_output() + list(input)) # reassign token and flush output token array
    lexer.Tokenize()
    
    parser.set_input(parser.reset_output() + lexer.get_output())
    parser.parse()

    print()
    print("Parser output: ")
    print(parser.get_output())
    print()
    print(parser.get_output()[0].get_params())
    print()

    interp.set_input(interp.reset_input() + parser.get_output())
    interp.Execute()
    

    


