from syntax.lexer import Lexer 
from syntax.parser import Parser 

class Interface: 
    
    def __init__(self):
        self.parser = Parser() 
        self.lexer = Lexer() 
    
    def get_parser(self):
        return self.parser
    
    def extract(self, origin_array, comparison_types):
        if not comparison_types:
            return []
        result = [token for token in origin_array() if any(token.type == ct.type for ct in comparison_types)]
        return result

