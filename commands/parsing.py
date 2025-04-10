import importlib
import importlib.util
import json
import os
import hashlib
from commands.command import command
from internal.web_crawler import WebCrawler
from internal.usage import usage
from dependencies.callback import Callback 
from dependencies.master import MasterDep
from syntax.types.TokenTypes import TokenTypes
from syntax.interface import interface

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config

env_config = load_config()

_callback = Callback()
TT = TokenTypes()
util = MasterDep()

def run_external_parser(parser_path, data):
    # Load the parser module from the specified path
    parser_name = parser_path.split("/|\\")[-1]
    spec = importlib.util.spec_from_file_location(parser_name, parser_path)
    parser_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser_module)

    # Execute the parser function if it exists
    if hasattr(parser_module, 'run_parser'):
        return getattr(parser_module, 'run_parser')(data)
    else:
        raise ImportError(f"The module {parser_name} at {parser_path} does not have a 'run_parser' function.")

def safe_file_name(url):
    """Generate a safe file name from the URL."""
    return hashlib.md5(url.encode('utf-8')).hexdigest() + '.txt'

def save_to_file(url, content):
    """Save the given content to a file in the 'output' directory if content is not empty."""
    if content:
        root_dir = 'output'
        os.makedirs(root_dir, exist_ok=True)  # Ensure the root directory exists
        file_path = os.path.join(root_dir, safe_file_name(url))
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Content saved to {file_path}")
    else:
        print(f"No content to save for URL: {url}")


def data(PARAMS):
    config = {"collect": False, "parse": False}
    search_engine_keywords = []
    
    # Parse command line parameters
    if not PARAMS:
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
            config["parse"] = ".\\external\\parser_template_one.py"
            parser_info = next((p for p in PARAMS[util.indexOf(PARAMS, flag_token) + 1:] if p.type != TT.Flag()), None)
            if parser_info:
                flag_contents = interface.extract_flags(PARAMS[util.indexOf(PARAMS, flag_token):])
                config["parse"] = flag_contents[0].get_value() if flag_contents else config["parse"]

    if not config["collect"]:
        print("Collect and parse not found")
        usage.display(usage.get_usage("data"))
        return _callback.catch("", False)
    
    # Execute web crawling and optional parsing
    web_crawler = WebCrawler(env_config['API_KEY'], env_config['CSE_ID'], search_engine_keywords)
    web_crawler.start_crawl_from_keywords()
    crawler_output = web_crawler.get_body()

    if config["parse"]:
        for url, output in crawler_output.items():
            parsed_output = run_external_parser(config["parse"], output)
            save_to_file(url, parsed_output)
    else:
        for url, output in crawler_output.items():
            save_to_file(url, output)

    return _callback.catch("", True)

command.add_func("data", data)

import os
import shutil

def reset_output_dir():
    """Remove all contents in the 'output' directory."""
    root_dir = 'output'
    try:
        # Check if the directory exists and remove all contents
        if os.path.exists(root_dir):
            shutil.rmtree(root_dir)
            print(f"All contents removed from {root_dir}.")
            # Optionally, recreate the directory after clearing it
            os.makedirs(root_dir, exist_ok=True)
            print(f"Reset {root_dir} directory.")
        else:
            print(f"No '{root_dir}' directory found, creating one.")
            os.makedirs(root_dir, exist_ok=True)
    except Exception as e:
        print(f"Failed to reset {root_dir}: {e}")

def reset_output(PARAMS):
    """CLI command function to handle resetting the output directory."""
    reset_output_dir()

# Register the reset command in your CLI framework
command.add_func("reset", reset_output)
