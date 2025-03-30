import re
from syntax.TokenTypes import TokenTypes

TT = TokenTypes()

class Lexer:
    def __init__(self):
        self.input = []
        self.token_output = []

    def get_input(self):
        return self.input 
    
    def set_input(self, new_input):
        self.input = new_input 
        return True

    def get_output(self):
        return self.token_output
    
    def reset_output(self):
        self.token_output = []
        return self.token_output

    def get_current(self): 
        if not len(self.get_input()):
            return None 
        return self.get_input()[0]
    
    def add_token(self, new_token):
        self.token_output.append(new_token)
        return True
    
    def consume(self):
        consumed = self.get_current()
        if not consumed:
            return consumed 
        self.set_input(self.get_input()[1:])
        return consumed
    
    def Tokenize(self):
        
        while self.get_current():
            consumed = self.consume()
            if not consumed:
                return consumed 

            if re.search(r'\s', consumed):
                return self.Tokenize()
            
            if re.search(r'=', consumed):
                self.add_token(TT.Assign())
                return self.Tokenize()

            if re.search(r'\"|\'', consumed):
                string = "" 
                while self.get_current() and not re.search('\"|\'', self.get_current()):
                    string += self.consume()
                self.add_token(TT.String(string))
                print("checkpoint: string")
                self.consume()
                return self.Tokenize()

            if re.search(r'[a-zA-Z]', consumed):
                command = consumed 
                while self.get_current() and re.search(r'[a-zA-Z0-9._-]', self.get_current()):
                    command += self.consume()
                self.add_token(TT.Command(command))
                print("checkpoint: command: "+ command)
                return self.Tokenize()
            
            if re.search(r'\-[a-zA-Z0-9_]|\[|\]', consumed + str(self.get_current())):
                flag = consumed
                while self.get_current() and re.search(r'[a-zA-Z0-9_]|\-', self.get_current()):
                    flag += self.consume()
                self.add_token(TT.Flag(flag))
                print("checkpoint: flag: "+ flag)
                return self.Tokenize()

            if re.search(r'\-\-', consumed + str(self.get_current())):
                global_flag = consumed
                while self.get_current() and re.search(r'[a-zA-Z0-9_]|\-', self.get_current()):
                    global_flag += self.consume()
                self.add_token(TT.GlobalFlag(global_flag))
                print("checkpoint: global flag: "+ global_flag)
                return self.Tokenize()
            
            if re.search(r'\d', consumed):
                number = consumed 
                while self.get_current() and re.search(r'\d|[.,]', self.get_current()):
                    number += self.consume()
                self.add_token(TT.Number(number))
                print("checkpoint: number")
                return self.Tokenize()
            
            if re.search(r'\(|\)', consumed):
                if consumed == ")":
                    self.add_token(TT.RParen())
                    self.Tokenize()

                if consumed == "(":
                    self.add_token(TT.LParen())
                    self.Tokenize()

            #self.add_token({ "type": "UNDEFINED", "value": None })
            
