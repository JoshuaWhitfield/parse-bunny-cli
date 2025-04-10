from internal.usage_object import UsageObject

class Usage:
    def __init__(self):
        self.body = {}

    def add_usage(self, cmd_name, usage_array, description, long, short):
        usage_object = UsageObject(cmd_name, usage_array, description, long, short)
        self.body[cmd_name] = usage_object
        return usage_object
    
    def get_usage(self, cmd_name):
        if cmd_name not in self.body:
            return None
        return self.body[cmd_name]
    
    def display(self, usage_object):
        # Fixing the join() issue for usage_array
        print("COMMAND: " + usage_object.get_name().upper())
        print(" " + "\n ".join(usage_object.get_usage_array()))  # Correct usage of join
        print(" desc: " + usage_object.get_description())
        print(" long: " + usage_object.get_long())
        if usage_object.get_short() != "":
            print(" short: " + usage_object.get_short())
        return True

# Example usage
usage = Usage()

usage.add_usage("clear", [" clear ", " cls "], "this command clears the terminal.", " clear ", " cls ")
usage.add_usage("data", [" data -collect['<string_keyword>', ...] ", " data -collect['<string_keyword>', ...] -parse['/full/path/to/parser'] ", " data -collect['<keywords>'] -parse[] "], "this command can collect and parse information for AI model training. by ommitting the path from the -parse flag, you use the built in parser.", " data ", "")
usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")
# Test displaying usage
