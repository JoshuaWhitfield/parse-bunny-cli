from internal.usage_object import UsageObject

class Usage:
    def __init__(self):
        self.body = {}

    def add_usage(self, cmd_name, usage_array, description, long, short):
        usage_object = UsageObject(cmd_name, usage_array, description, long, short)
        self.body[cmd_name] = usage_object
        return usage_object
    
    def get_usage(self, cmd_name):
        if not cmd_name in self.body.keys():
            return None
        return self.body[cmd_name]
    
    def display(self, usage_object):
        print(usage_object.get_name().upper() + ": ")
        print(" " + usage_object.get_usage_array.join("\n "))
        print(" desc: " + usage_object.get_description())
        print(" long: " + usage_object.get_long())
        print(" short: " + usage_object.get_short())
        return True 
    
Usage.add_usage("clear", [" clear ", " cls "], "this command clears the terminal.", " clear ", " cls ")
Usage.add_usage("data", [" data [-collect | -parse] -template[<your_template>|std] -search-engine['<string_keyword>'] "], "this command can collect and parse information based on a template")




    
        
