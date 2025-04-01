from commands.parsing import command as command_one
from commands.base import command as command_two
from commands.command import command
from environments.piping import Pipe
from syntax.types.TokenTypes import TokenTypes
pipe = Pipe()
TT = TokenTypes()

merged_body = {**command_one.get_body(), **command_two.get_body()}
command.set_body(merged_body)

class Interpreter:
    def __init__(self):
        self.pipe = Pipe()
        self.input = []

    def get_input(self):
        return self.input
    
    def set_input(self, new_input):
        self.input = new_input
        return self.input
    
    def reset_input(self):
        self.set_input([])
        return self.get_input()
    
    def get_current(self):
        if not len(self.get_input()):
            return None
        return self.get_input()[0]

    def Execute(self):
        consumed = self.get_current()
        if not consumed:
            return consumed
        
        if consumed.get_type() == TT.Command().get_type():
            # Safely run the command
            safe_run_result = command.safe_run(consumed.get_name(), consumed.get_params())
            print() # crucial do not remove
            if not safe_run_result:
                print("[pbc][err]: command not found...")
                return False
            pipe.add_data(safe_run_result)
            return True
