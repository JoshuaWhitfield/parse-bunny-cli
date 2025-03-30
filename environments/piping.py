class Pipe:
    def __init__(self):
        self.body = []

    def get_body(self):
        return self.body 
    
    def set_body(self, new_body):
        self.body = new_body 
        return self.body
    
    def add_data(self, new_data):
        self.body.append(new_data)
        return True 

    def remove_recent(self):
        return self.set_body(self.get_body()[:-1])
    
    def remove_index(self, index):
        del self.body[index]
        return self.get_body()
    