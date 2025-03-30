import os
from commands.command import command
from dependencies.callback import Callback 
from internal.usage import Usage
from syntax.interface import Interface
from syntax.TokenTypes import TokenTypes
from dependencies.master import MasterDep

_callback = Callback()
interface = Interface()
TT = TokenTypes()
util = MasterDep()

def clear(PARAMS):
    os.system('cls' if os.name == 'nt' else 'clear')
    return _callback.catch("", True)
command.add_func('clear', clear)
command.add_func('cls', clear)

def data(PARAMS):
    config = {"collect": False, "parse": False}
    collect = {"template": False}
    def init():
        if not len(PARAMS):
            Usage.display(Usage.get_usage("data"))
            return _callback.catch("", False)
        
        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        if not len(flag_tokens):
            Usage.display(Usage.get_usage("data"))
            return _callback.catch("", False)
        
        for flag_token in flag_tokens:
            if util.indexOf(["collect", "c"], flag_token.value.remove("-", "")) > -1:
                config.collect = True

            if util.indexOf(["parse", "p"], flag_token.value.remove("-", "")) > -1:
                config.parse = True