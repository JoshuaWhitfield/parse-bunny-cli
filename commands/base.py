from dependencies.callback import Callback
from commands.command import command 
from syntax.interface import interface
import os

_callback = Callback()

def clear(PARAMS):
    os.system('cls' if os.name == 'nt' else 'clear')
    return _callback.catch("", True)
command.add_func('clear', clear)
command.add_func('cls', clear)

def exit(PARAMS):
    interface.end_process()
    return _callback.catch("", True)
command.add_func('exit', exit)