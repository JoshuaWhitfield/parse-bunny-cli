from environments.piping import Pipe
from dependencies.master import MasterDep

util = MasterDep()

class CommandInterface:
    def __init__(self):
        self.pipe = Pipe()

    def load_flag_logic(self, func_body, config):
        return func_body(config)
    
    def append_pipe(self, new_item):
        self.pipe.add_data(new_item)
        return new_item

    def rm_prev(self):
        if not len(self.pipe.get_body()):
            return None
        self.pipe.remove_recent()
        return True

    def rm_index(self, index):
        if not len(self.pipe.get_body()):
            return None
        self.pipe.remove_index(index)
        return True
    
    
interface = CommandInterface()