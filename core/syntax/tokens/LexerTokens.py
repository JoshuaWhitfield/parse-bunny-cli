class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def get_type(self):
        return self.type 

    def get_value(self):
        return self.value
    
    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}')"