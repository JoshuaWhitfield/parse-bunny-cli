import os
from commands.command import command
from dependencies.callback import Callback 
from internal.usage import usage
from syntax.interface import Interface
from syntax.TokenTypes import TokenTypes
from dependencies.master import MasterDep
from internal.web_crawler import WebCrawler

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
    collect = {"template": False, "search_engine": False}
    search_engine_keywords = []  # List to store search engine keywords

    def init():
        if not len(PARAMS):
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        # Extract URL tokens and validate if they are valid URLs
        url_tokens = interface.extract(PARAMS, [TT.String()])
        if not len(url_tokens):
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)

        # Extract only valid URLs (starting with http:// or https://)
        config["url"] = [token.value for token in url_tokens if token.value.startswith("http://") or token.value.startswith("https://")]

        # If no valid URLs are found, return an error message
        if not config["url"]:
            print("No valid URLs provided. Please provide URLs starting with http:// or https://.")
            return _callback.catch("", False)

        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        if not len(flag_tokens):
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)

        for flag_token in flag_tokens:
            if util.indexOf(["collect", "c"], flag_token.value.replace("-", "")) > -1:
                config["collect"] = True

            if util.indexOf(["parse", "p"], flag_token.value.replace("-", "")) > -1:
                config["parse"] = True

            if util.indexOf(["searchengine", "s"], flag_token.value.replace("-", "")) > -1:
                collect["search_engine"] = True
                flag_contents = interface.extract_flags(PARAMS[util.indexOf(PARAMS, flag_token):])
                for token in flag_contents:
                    search_engine_keywords.append(token.get_value())

            if util.indexOf(["template", "t"], flag_token.value.replace("-", "")) > -1:
                collect["template"] = True

        if not config["collect"] and not config["parse"]:
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        if not collect["template"] or not collect["search_engine"]:
            usage.display(usage.get_usage("data"))
            return _callback.catch("", False)
        
        return _callback.catch("", True)
    
    error_handling = init()
    if not error_handling.get_status():
        return error_handling

    # Now that we've filtered the URLs, process them
    for url in config["url"]:
        web_crawler = WebCrawler(keywords=search_engine_keywords)  # Pass the keywords to the crawler
        web_crawler.crawl(url, 0, 20)
        print()
        print(f"Web crawl completed at {url} ...")
        print(f"body content: \n{web_crawler.get_body()}")
        print()

    return _callback.catch(web_crawler.get_body(), True)
command.add_func("data", data)
