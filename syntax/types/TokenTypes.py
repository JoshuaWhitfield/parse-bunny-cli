from syntax.tokens.LexerTokens import Token 

class TokenTypes:
    
    def Command(self, value = None):
        return Token("COMMAND", value)
    
    def String(self, value = None):
        return Token("STRING", value)
    
    def Flag(self, value = None):
        return Token("FLAG", value)
    
    def GlobalFlag(self, valuqe = None):
        return Token("GLOBALFLAG", value)
    
    def Macro(self, value = None):
        return Token("MACRO", value)
    
    def Number(self, value = None):
        return Token("NUMBER", value)
    
    def LParen(self):
        return Token("LPAREN", "(")
    
    def RParen(self):
        return Token("RPAREN", ")")
    
    def Assign(self):
        return Token("ASSIGN", "=")