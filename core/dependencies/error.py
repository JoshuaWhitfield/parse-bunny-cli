class Error:
    def __init__(self, data, status):
        self.status = status 
        self.data = data

    def get_data(self):
        return self.data 
    
    def get_status(self):
        return self.status