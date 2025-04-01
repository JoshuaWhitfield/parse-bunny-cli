import os
from commands.command import command
from dependencies.callback import Callback 
from internal.usage import usage
from syntax.interface import Interface
from syntax.TokenTypes import TokenTypes
from dependencies.master import MasterDep
from internal.web_crawler import WebCrawler
import importlib
import importlib.util

import json

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config

env_config = load_config()

_callback = Callback()
interface = Interface()
TT = TokenTypes()
util = MasterDep()

def clear(PARAMS):
    os.system('cls' if os.name == 'nt' else 'clear')
    return _callback.catch("", True)
command.add_func('clear', clear)
command.add_func('cls', clear)


def run_external_parser(parser_path, data):
    # Attempt to load the module from the given file location
    parser_name = parser_path.split("/|\\")[-1]
    spec = importlib.util.spec_from_file_location(parser_name, parser_path)
    parser_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser_module)

    # Check if the 'run_parser' function exists in the loaded module
    if hasattr(parser_module, 'run_parser'):
        parser_function = getattr(parser_module, 'run_parser')
        return parser_function(data)  # Execute the parser function and pass the web crawler's output
    else:
        raise ImportError(f"The module {parser_name} at {parser_path} does not have a 'run_parser' function.")


def data(PARAMS):
    config = {"collect": False, "parse": False, "url": False, "parser_path": None}
    collect = {"search_engine": False}
    search_engine_keywords = []
    
    def init():
        if not len(PARAMS):
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)

        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        for flag_token in flag_tokens:
            cleaned_token_value = flag_token.value.replace("-", "")
            if util.indexOf(["collect", "c"], cleaned_token_value) > -1:
                config["collect"] = True
                flag_contents = interface.extract_flags(PARAMS[util.indexOf(PARAMS, flag_token):])
                for token in flag_contents:
                    search_engine_keywords.append(token.get_value())

            if util.indexOf(["parse", "p"], cleaned_token_value) > -1:
                config["parse"] = True
                parser_info = next((p for p in PARAMS[PARAMS.index(flag_token) + 1:] if p.type != TT.Flag()), None)
                if parser_info:
                    flag_contents = interface.extract_flags(PARAMS[util.indexOf(PARAMS, flag_token):])
                    if not len(flag_contents):
                        config["parser_path"] = ".\\external\\parser_template_one.py"
                    else:
                        config["parser_path"] = flag_contents[0].get_value()

                    
                else:
                    usage.display(usage.get_usage("data"))
                    return _callback.catch("", False)

        if not config["collect"]:
            print("collect and parse not found")
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        return _callback.catch("", True)

    error_handling = init()
    if not error_handling.get_status():
        return error_handling
    
    if config["collect"]:
        api_key = env_config['API_KEY']
        cse_id = env_config['CSE_ID']
        web_crawler = WebCrawler(api_key=api_key, cse_id=cse_id, keywords=search_engine_keywords)
        web_crawler.start_crawl_from_keywords()
        crawler_output = web_crawler.get_body()  # Assuming get_body() returns the data you want to process
        # Check if a parser is specified and if so, process the crawler output with it
        if config["parser_path"]:
            for link in crawler_output.values():
                parser_output = run_external_parser(config["parser_path"], link)
                print("\n\nParser Output:", parser_output)
        else:
            print("\n\nCrawler Output:", crawler_output)

    # Continue with regular operations if all checks pass

    return _callback.catch(web_crawler.get_body(), True)
command.add_func("data", data)


def db(PARAMS):
    config = {"show": False}
    def init():
        if not len(PARAMS):
            usage.display(usage.get_usage("db"))
            return _callback.catch("", False)
        
        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        if not len(flag_tokens):
            usage.display(usage.get_usage("db"))
            return _callback.catch("[db][err]: flags must be in use...", False)

        for flag_token in flag_tokens:
            if util.indexOf(["[", "]"], flag_token.value.replace("-", "")) > -1:
                continue 
            
            if util.indexOf(["show", "shw"], flag_token.value.replace("-", "")) > -1:
                config["show"] = True 
            
        if not config["show"]:
            usage.display(usage.get_usage("db"))
            return _callback.catch("[db][err]: invalid flag...", False)
        
        return _callback.catch("", True)
    
    error_handling = init()
    if not error_handling.status:
        return error_handling
    
    print("[parse][bunny][sys]: in development. need funding, WSL for Redis wont run on my laptop.")
    
    return _callback.catch("", True)
command.add_func("db", db) 
    