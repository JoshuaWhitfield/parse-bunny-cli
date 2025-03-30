from dependencies.master import MasterDep as Util
from dependencies.callback import Callback
from syntax.ParserTypes import ParserTypes
from syntax.TokenTypes import TokenTypes

util = Util()
_callback = Callback()
PT = ParserTypes()
TT = TokenTypes()

class Parser:
    def __init__(self):
        self.input = []
        self.token_output = []

    def get_input(self):
        return self.input

    def set_input(self, new_input):
        self.input = new_input
        return True

    def get_current(self):
        if not len(self.get_input()):
            return None
        return self.get_input()[0]

    def add_token(self, new_token):
        self.token_output.append(new_token)
        return True

    def get_output(self):
        return self.token_output

    def reset_output(self):
        self.token_output = []
        return self.token_output

    def extract(self, comparison_types = []):
        if not comparison_types:
            return []
        result = [token for token in self.get_input() if any(token.type == ct.type for ct in comparison_types)]
        return result

    def parse(self):
        # handle commands, variables, and functions
        
        command_tokens = self.extract([TT.Command()])
        if len(command_tokens):
            # handle variable assign or lookup
            variable_tokens = self.extract([TT.Assign(), TT.Number(), TT.String(), TT.Command(), TT.LParen(), TT.RParen()])
            variable_index = -1
            found = False 
            
            for lexer_token in self.get_input():
                variable_index += 1
                if lexer_token.get_type() == TT.Command().get_type():
                    found = True
                    break

            if found: 
                if variable_index != -1:
                    variable_name = variable_tokens[variable_index].value
                    if len(variable_tokens):
                        if len(self.extract([TT.Assign()])):
                            if len(variable_tokens) == 3:
                                self.add_token(PT.VariableAssignment(variable_name, variable_tokens[1:]))
                                return None  # Corrected slice
                            if len(self.extract([TT.Command()])):
                                self.add_token(PT.VariableLookup(variable_name))  # variable lookups will be checked for command existence in interpreter runtime.
                                return None
                
            # handle function call
            paren_tokens = self.extract([TT.LParen(), TT.RParen()])
            if len(paren_tokens) > 0:
                if len(paren_tokens) == 1 and paren_tokens[0].get_type() == TT.RParen().get_type():
                    print()
                    print("[syntax][err]: parameters without ending parenthesis...")
                    print()
                    return False

                if len(paren_tokens) == 1 and paren_tokens[0].get_type() == TT.LParen().get_type():
                    print()
                    print("[syntax][err]: parameters without starting parenthesis...")
                    print()
                    return False

                paren_toggle = False
                params_array = []
                last_idx = -1

                print("point input: " + str(self.get_input()))
                for lexer_token in self.get_input():
                    last_idx += 1
                    if lexer_token.get_type() == TT.RParen().get_type():
                        print("EXITING...")
                        break
                    if lexer_token.get_type() == TT.LParen().get_type():
                        print("toggle engaged...")
                        paren_toggle = True
                        continue
                    if paren_toggle:
                        print("appending repr token...")
                        params_array.append(lexer_token)  # Use append instead of push
                    
                print("<color=green> params_array: "+ str(params_array))
                self.add_token(PT.funcCall(command_tokens[0].get_value(), [params_array, self.get_input()[last_idx + 1:]]))
                return None

            # handle commands
            self.add_token(PT.Command(command_tokens[0].get_value(), self.get_input()[1:]))
            return None
