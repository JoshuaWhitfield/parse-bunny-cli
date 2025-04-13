import os
from environments.piping import Pipe
from dependencies.callback import Callback
from commands.interface import CommandInterface

pipe = Pipe()
_callback = Callback()
CI = CommandInterface()

class Command:
    def __init__(self):
        self.body = {}
        self.interface = CommandInterface()

    def get_body(self): 
        return self.body 
    
    def set_body(self, new_body):
        self.body = new_body

    def add_func(self, cmd_name, func_body):
        self.body[cmd_name] = func_body

    def safe_run(self, name, PARAMS, add_to_pipe=False):
        # Check if the command exists in the body
        if name not in self.body:
            return False
        
        # Retrieve the function to be executed
        func = self.body[name]

        if add_to_pipe:
            # Execute the function and handle the result
            safe_run_result = func(PARAMS)
            if not safe_run_result.status:
                print(safe_run_result.data)
                return False
            pipe.add_data(safe_run_result)
            return True
        
        # If no pipe addition is needed, just run the function
        return func(PARAMS)


command = Command()



