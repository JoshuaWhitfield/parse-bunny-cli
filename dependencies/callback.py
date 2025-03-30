import json 

class Callback:

    def __init__(self):
        self.toggle = False

    def catch(self, message = "", status = 0):
        return { "status": status, "data": message }
    
    def toggle_debug(self):
        self.toggle = not self.toggle
        return self.toggle
    
    def debug(self, data, location, line_number):
        debug_content = { "content": data, "location": location, "line": line_number }
        if self.toggle:
            print(json.dump(debug_content))
        return debug_content

    def local_debug(self, data, location, line_number):
        self.toggle_debug()
        debug_result = self.debug(data, location, line_number)
        self.toggle_debug()
        return debug_result 
