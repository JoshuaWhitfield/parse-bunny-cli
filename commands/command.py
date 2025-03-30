import os
from environments.piping import Pipe
from dependencies.callback import Callback

pipe = Pipe()
_callback = Callback()

class Command:
    def __init__(self):
        self.body = {}

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

def grab(PARAMS):
    def init():
        if not len(PARAMS):
            return 


