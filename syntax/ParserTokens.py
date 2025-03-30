class ParserToken:
    def __init__(self, type, name, params = None):
        self.type = type
        self.name = name 
        self.params = params 

    def get_type(self):
        return self.type 

    def get_name(self):
        return self.name
    
    def get_params(self):
        return self.params