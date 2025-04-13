class UsageObject:
    def __init__(self, cmd_name, usage_array, description, long, short):
        self.cmd_name = cmd_name 
        self.usage_array = usage_array
        self.description = description
        self.long = long 
        self.short = short 

    def get_name(self):
        return self.cmd_name 
    
    def get_usage_array(self):
        return self.usage_array
    
    def get_description(self):
        return self.description
    
    def get_long(self):
        return self.long 
    
    def get_short(self):
        return self.short

    