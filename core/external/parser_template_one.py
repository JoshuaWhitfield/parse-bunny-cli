import re

class Parser:
    def __init__(self):
        self.output = ""
        self.input = ""
        self.capture_toggle = False 

    def set_toggle(self, bool = False):
        self.capture_toggle = bool

    def get_toggle(self):
        return self.capture_toggle
    
    def get_input(self):
        return self.input 
    
    def set_input(self, new_input):
        self.input = new_input
        return self.input

    def get_current(self):
        if not len(self.get_input()):
            return None 
        return self.get_input()[0]
    
    def get_current_text(self):
        if not len(self.get_text()):
            return None 
        return self.get_text()
    
    def get_output(self):
        return self.output
    
    def add_output(self, output):
        self.output += " " + output
        return True

    def consume(self):
        if not self.get_current():
            return None
        result = self.get_input()[0]
        self.set_input(self.get_input()[1:])
        return result

    def parse(self):
        while self.get_current():
            consumed = self.consume()
            if not consumed:
                return consumed
            if re.search(r"\>|\'", consumed) or re.search(r'\"', consumed) or re.search(r'\.', consumed):
                output = ""
                while self.get_current() and (not re.search(r"\'|\<", self.get_current()) or not re.search(r'\"', self.get_current() or not re.search(r'\.', consumed))):
                    output += self.consume()
                self.add_output(output)
                return self.parse()

def run_parser(input):
    parser = Parser()
    # exit(type(input))
    parser.set_input(input)
    parser.parse()
    return parser.get_output()