import os
from commands.command import command
from dependencies.callback import Callback 
from internal.usage import usage
from syntax.interface import Interface
from syntax.TokenTypes import TokenTypes
from dependencies.master import MasterDep
from internal.web_crawler import WebCrawler

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

def data(PARAMS):
    config = {"collect": False, "parse": False, "url": False}
    collect = {"search_engine": False}
    search_engine_keywords = []  # List to store search engine keywords

    def init():
        if not len(PARAMS):
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        if not len(flag_tokens):
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)

        for flag_token in flag_tokens:
            if util.indexOf(["[", "]"], flag_token.value) > -1:
                continue
            cleaned_token_value = flag_token.value.replace("-", "")
            if util.indexOf(["collect", "c"], cleaned_token_value) > -1:
                config["collect"] = True

            if util.indexOf(["parse", "p"], cleaned_token_value) > -1:
                config["parse"] = True

            if util.indexOf(["searchengine", "s"], cleaned_token_value) > -1:
                # _callback.local_debug(cleaned_token_value, "parsing:", 59)
                collect["search_engine"] = True
                flag_contents = interface.extract_flags(PARAMS[util.indexOf(PARAMS, flag_token):])
                for token in flag_contents:
                    search_engine_keywords.append(token.get_value())

        if not config["collect"] and not config["parse"]:
            print("collect and parse not found")
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        if not collect["search_engine"]:
            print("search engine not found")
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        return _callback.catch("", True)
    
    error_handling = init()
    if not error_handling.get_status():
        return error_handling

    # Now that we've filtered the URLs, process them
    api_key = env_config['API_KEY']
    cse_id = env_config['CSE_ID']

    web_crawler = WebCrawler(api_key=api_key, cse_id=cse_id, keywords=search_engine_keywords)  # Pass the keywords to the crawler
    web_crawler.start_crawl_from_keywords()
    print()
    _callback.local_debug(web_crawler.get_body(), "parsing:", 83)
    print()

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
    

    
    return _callback.catch("", True)
command.add_func("db", db) 
    