import importlib
import importlib.util
import json
import shutil
import os
import re
import hashlib
from datetime import datetime
from commands.command import command
from internal.web_crawler import WebCrawler
from internal.usage import usage
from dependencies.callback import Callback 
from dependencies.master import MasterDep
from syntax.types.TokenTypes import TokenTypes
from syntax.interface import interface
from glob import glob
import imaplib

import uuid
from pathlib import Path
from datetime import datetime
import requests
from PyPDF2 import PdfReader
import docx
import email
from email import policy

from backend.utils.db import insert_log

def normalize_path(path_str):
    """
    Normalize a given path string to a proper Path object.
    Handles raw strings, environment variables, and Windows-style backslashes.
    """
    # Remove wrapping quotes if present
    if path_str.startswith(("'", '"')) and path_str.endswith(("'", '"')):
        path_str = path_str[1:-1]

    # Expand ~ and environment variables
    expanded = os.path.expandvars(os.path.expanduser(path_str))

    # Normalize and convert to absolute path
    return Path(expanded).resolve()

import pkgutil

def load_config():
    data = pkgutil.get_data("commands", "config.json")
    return json.loads(data.decode("utf-8"))

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

def save_ingested_content(text, out_folder, source_path):
    os.makedirs(out_folder, exist_ok=True)

    # Generate MD5 hash from content
    md5 = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]

    # Clean original file name (remove extension and slashes)
    original_name = Path(source_path).stem 
    output_name = f"{original_name}_{md5}.txt"

    # Save to file

    output_path = Path(out_folder) / output_name
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Source: {source_path}\n")
        f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
        f.write(text.strip())

    print(f"[ingest][+] Saved: {output_name}")

def ingest_pdfs_from(path, out_folder):
    for file in Path(path).rglob("*.pdf"):
        try:
            reader = PdfReader(str(file))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            save_ingested_content(text, out_folder, file)
        except Exception as e:
            print(f"[ingest][x] PDF failed: {file} → {e}")


def ingest_docx_from(path, out_folder):
    for file in Path(path).rglob("*.docx"):
        try:
            doc = docx.Document(str(file))
            text = "\n".join(p.text for p in doc.paragraphs)
            save_ingested_content(text, out_folder, file)
        except Exception as e:
            print(f"[ingest][x] DOCX failed: {file} → {e}")


def ingest_emails_from(path, out_folder):
    for file in Path(path).rglob("*.eml"):
        try:
            with open(file, "rb") as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode(errors="ignore")
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                save_ingested_content(body, out_folder, file)
        except Exception as e:
            print(f"[ingest][x] EML failed: {file} → {e}")

def ingest(PARAMS):
    config = {
        "pdf": [],
        "doc": [],
        "email": [],
        "output": ".\\data\\ingested\\"
    }

    if not PARAMS:
        usage.display(usage.get_usage("ingest"))
        return _callback.catch("", False)

    flag_tokens = interface.extract(PARAMS, [TT.Flag()])
    for flag_token in flag_tokens:
        cleaned = flag_token.value.replace("-", "")
        index = util.indexOf(PARAMS, flag_token)

        if util.indexOf(["pdf"], cleaned) > -1:
            flag_contents = interface.extract_flags(PARAMS[index:])
            config["pdf"] += [token.get_value() for token in flag_contents]

        if util.indexOf(["doc"], cleaned) > -1:
            flag_contents = interface.extract_flags(PARAMS[index:])
            config["doc"] += [token.get_value() for token in flag_contents]

        if util.indexOf(["email"], cleaned) > -1:
            flag_contents = interface.extract_flags(PARAMS[index:])
            config["email"] += [token.get_value() for token in flag_contents]

        if util.indexOf(["output", "o"], cleaned) > -1:
            flag_contents = interface.extract_flags(PARAMS[index:])
            if flag_contents:
                config["output"] = normalize_path(flag_contents[0].get_value())

    if not (config["pdf"] or config["doc"] or config["email"]):
        print("[ingest][x]: no input sources provided.")
        usage.display(usage.get_usage("ingest"))
        return _callback.catch("", False)

    print(f"[ingest][✓]: output folder → {config['output']}")

    for folder in config["pdf"]:
        ingest_pdfs_from(folder, config["output"])

    for folder in config["doc"]:
        ingest_docx_from(folder, config["output"])

    for folder in config["email"]:
        ingest_emails_from(folder, config["output"])

    return _callback.catch("[ingest][✓]: finished ingestion", True)
command.add_func("ingest", ingest)

def deepseek_label(text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[label][x]: missing OPENAI_API_KEY")
        print("please visit platform.deepseek.com/api_keys and create an api key")
        print("then copy it, and run in terminal:")
        print("> $env:OPENAI_API_KEY = 'YOUR_API_KEY'")
        return None

    label_set = (
        "contract, nda, invoice, email, resume, report, policy, legal_notice, "
        "statement, transcript, form, other"
    )

    prompt = (
        f"What kind of document is this? Only respond with one of the following labels:\n{label_set}.\n\n"
        + text[:3000]
    )

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
    )

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"].strip().lower()
        return {
            "label": content,
            "confidence": 0.95  # optionally parse for confidence if DeepSeek returns one
        }
    else:
        print(f"[label][x]: API error {response.status_code}")
        return None

def label(PARAMS):
    config = {
        "files": [],
        "name": None
    }

    if not PARAMS:
        usage.display(usage.get_usage("label"))
        return _callback.catch("", False)

    # Parse flags
    flag_tokens = interface.extract(PARAMS, [TT.Flag()])
    for flag_token in flag_tokens:
        cleaned = flag_token.value.replace("-", "")
        index = util.indexOf(PARAMS, flag_token)

        if cleaned == "files":
            flag_contents = interface.extract_flags(PARAMS[index:])
            for token in flag_contents:
                val = token.get_value()
                path = normalize_path(val)

                if "*" in val:
                    config["files"] += [str(p) for p in glob(val, recursive=True) if Path(p).is_file()]
                elif path.is_file():
                    config["files"].append(str(path))
                elif path.is_dir():
                    config["files"] += [str(p) for p in path.rglob("*.txt")]

        elif cleaned == "name":
            flag_contents = interface.extract_flags(PARAMS[index:])
            if flag_contents:
                config["name"] = flag_contents[0].get_value()

    if not config["files"]:
        print("[label][x]: no valid files provided.")
        return _callback.catch("", False)

    if not config["name"]:
        print("[label][x]: missing -name[...] flag.")
        return _callback.catch("", False)

    # Label all files
    output_path = Path("data/classified")
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"{config['name']}.json"

    results = []
    for file_path in config["files"]:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            label_data = deepseek_label(text)

            if label_data:
                results.append({
                    "file": Path(file_path).name,
                    "label": label_data.get("label"),
                    "confidence": label_data.get("confidence"),
                    "model": "deepseek"
                })
                print(f"[label][✓]: {Path(file_path).name} → {label_data['label']}")
            else:
                print(f"[label][x]: failed to label {file_path}")

        except Exception as e:
            print(f"[label][x]: error with {file_path} → {e}")

    # Append if file already exists
    if output_file.exists():
        try:
            existing = json.loads(output_file.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                results = existing + results
        except Exception as e:
            print(f"[label][warn]: could not load existing {output_file.name}, overwriting...")

    # Save updated results
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    insert_log("label", {
        "params": [
            config["files"],
            config["name"]
        ],
        "results": results  # if you want to store results too
    })

    return _callback.catch(f"[label][✓]: saved to {output_file.name}", True)

command.add_func("label", label)
command.add_func("lbl", label)

def extract(PARAMS):
    config = {
        "files": [],
        "template": "full_terms",
        "name": None
    }

    if not PARAMS:
        usage.display(usage.get_usage("extract"))
        return _callback.catch("", False)

    # Parse flags
    flag_tokens = interface.extract(PARAMS, [TT.Flag()])
    for flag_token in flag_tokens:
        cleaned = flag_token.value.replace("-", "")
        index = util.indexOf(PARAMS, flag_token)

        if cleaned == "files":
            flag_contents = interface.extract_flags(PARAMS[index:])
            for token in flag_contents:
                value = token.get_value()
                path = normalize_path(value)
                if "*" in value:
                    config["files"] += [str(p) for p in glob(value, recursive=True) if Path(p).is_file()]
                elif path.is_file():
                    config["files"].append(str(path))
                elif path.is_dir():
                    config["files"] += [str(p) for p in path.rglob("*.txt")]

        elif cleaned == "template":
            flag_contents = interface.extract_flags(PARAMS[index:])
            if flag_contents:
                config["template"] = flag_contents[0].get_value()

        elif cleaned == "name":
            flag_contents = interface.extract_flags(PARAMS[index:])
            if flag_contents:
                config["name"] = flag_contents[0].get_value()

    if not config["files"]:
        print("[extract][x]: no valid files provided.")
        return _callback.catch("", False)

    if not config["template"]:
        print("[extract][x]: missing -template[...] flag.")
        return _callback.catch("", False)

    # Load template
    template_file = normalize_path(f"./data/templates/{config['template']}.json")
    if not template_file.exists():
        print(f"[extract][x]: template not found → {template_file}")
        return _callback.catch("", False)

    with open(template_file, "r", encoding="utf-8") as f:
        template = json.load(f)

    # Begin extraction
    results = []
    for file_path in config["files"]:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            extracted = {}

            for clause in template:
                key = clause.get("key")
                pattern = clause.get("pattern")
                if not key or not pattern:
                    continue

                lines = text.splitlines()
                for i, paragraph in enumerate(lines):
                    if re.search(pattern, paragraph, flags=re.IGNORECASE):
                        extracted[key] = {
                            "text": paragraph.strip(),
                            "line": i + 1
                        }
                        break

            results.append({
                "file": Path(file_path).name,
                "extracted": extracted
            })

            print(f"[extract][✓]: {Path(file_path).name} → {len(extracted)} fields")

        except Exception as e:
            print(f"[extract][x]: error with {file_path} → {e}")

    # Save extraction output
    output_dir = Path("./data/extracted")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = config["name"]
    out_file = output_dir / f"{output_name}.json"

    # If file already exists, load and append
    if out_file.exists():
        try:
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                results = existing + results
        except Exception as e:
            print(f"[extract][warn]: could not load existing {out_file.name}, overwriting...")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return _callback.catch(f"[extract][✓]: saved to {out_file.name}", True)

command.add_func("extract", extract)

import re
from pathlib import Path
import glob

def search(PARAMS):
    config = {
        "files": [],
        "label": [],
        "extract": [],
        "text": [],
        "name": None
    }

    if not PARAMS:
        usage.display(usage.get_usage("search"))
        return _callback.catch("", False)

    # Parse flags
    flag_tokens = interface.extract(PARAMS, [TT.Flag()])
    for flag_token in flag_tokens:
        cleaned = flag_token.value.replace("-", "")
        index = util.indexOf(PARAMS, flag_token)
        flag_contents = interface.extract_flags(PARAMS[index:])

        if cleaned == "files":
            for token in flag_contents:
                val = token.get_value()
                path = Path(val)
                # Recurse if directory or process if it's a file
                if "*" in val:
                    config["files"] += [f for f in glob.glob(val, recursive=True) if Path(f).is_file()]
                elif path.is_file():
                    config["files"].append(str(path))
                elif path.is_dir():
                    config["files"] += [str(p) for p in path.rglob("*") if p.is_file()]

        elif cleaned == "label":
            config["label"] += [token.get_value().lower() for token in flag_contents]

        elif cleaned == "extract":
            config["extract"] += [token.get_value() for token in flag_contents]

        elif cleaned == "text":
            config["text"] += [token.get_value().lower() for token in flag_contents]

        elif cleaned == "name":
            if flag_contents:
                config["name"] = flag_contents[0].get_value()

    if not config["files"]:
        print("[search][x]: no valid file(s) found to search")
        return _callback.catch("", False)

    results = []

    for file_path in config["files"]:
        try:
            # Read the content of the file (assuming plain text or any non-JSON format)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # If the file is empty, skip it
            if not content:
                print(f"[search][x]: {file_path} is empty, skipping.")
                continue

            match_types = []
            matches = []

            # Optional: get source text for line lookup
            lines = content.splitlines()

            # Label match
            if config["label"]:
                label_val = ""  # Assuming no direct "label" in plain text files
                for label in config["label"]:
                    if label in content.lower():
                        match_types.append("label")
                        matches.append({
                            "key": "label",
                            "text": label,
                            "line": -1
                        })

            # Extract match
            if config["extract"]:
                for condition in config["extract"]:
                    if "=" in condition:
                        key, val = map(str.strip, condition.split("=", 1))
                        # Assuming extracted data would be a part of the content, like a key:value pair
                        if key in content and val.lower() in content.lower():
                            match_types.append(key)
                            match_line = next((i+1 for i, line in enumerate(lines) if val.lower() in line.lower()), -1)
                            matches.append({
                                "key": key,
                                "text": content,
                                "line": match_line
                            })

            # Regex search in text
            if config["text"]:
                for search_term in config["text"]:
                    regex = re.compile(search_term, re.IGNORECASE)
                    for line_num, line in enumerate(lines):
                        if regex.search(line):
                            match_types.append("text")
                            matches.append({
                                "key": "text",
                                "text": line.strip(),
                                "line": line_num + 1
                            })

            if match_types:
                results.append({
                    "file": file_path,
                    "match_type": match_types,
                    "matches": matches
                })

        except Exception as e:
            print(f"[search][x]: failed to parse {file_path} → {e}")

    # Save results
    search_dir = Path("data/search")
    search_dir.mkdir(parents=True, exist_ok=True)
    output_name = config.get("name") or "results"
    output_file = search_dir / f"{output_name}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[search][✓]: found {len(results)} match(es). Saved to {output_file.name}")
    return _callback.catch("", True)

command.add_func("search", search)

REDACT_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "date": r"\b(?:\d{1,2}[-/th|st|nd|rd\s]*)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[-\s]?\d{1,4}\b|\b\d{4}-\d{2}-\d{2}\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
}

def deepseek_redact(text, matches):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[redact][x]: missing OPENAI_API_KEY")
        print("please visit platform.deepseek.com/api_keys and create an api key")
        print("then copy it, and run in terminal:")
        print("> $env:OPENAI_API_KEY = 'YOUR_API_KEY'")
        return text

    prompt = (
        f"Redact all personal {", ".join(matches)}, and sensitive legal identifiers from this text."
        " Return the redacted text with '[REDACTED]' in place of any sensitive info.\n\nText:\n" + text
    )

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print(f"[redact][x]: API error {response.status_code}")
        return text

def redact(PARAMS):
    config = {
        "files": [],
        "tags": []
    }

    if not PARAMS:
        usage.display(usage.get_usage("redact"))
        return _callback.catch("", False)

    flag_tokens = interface.extract(PARAMS, [TT.Flag()])
    for flag_token in flag_tokens:
        cleaned = flag_token.value.replace("-", "")
        index = util.indexOf(PARAMS, flag_token)
        flag_contents = interface.extract_flags(PARAMS[index:])

        if cleaned == "files":
            for token in flag_contents:
                val = token.get_value()
                p = Path(val)
                if p.is_dir():
                    config["files"] += [str(f) for f in p.rglob("*.txt") if f.is_file()]
                elif "*" in val:
                    config["files"] += [f for f in glob(val, recursive=True) if Path(f).is_file()]
                elif p.is_file():
                    config["files"].append(str(p))

        elif cleaned == "tags":
            config["tags"] += [token.get_value().lower() for token in flag_contents]

    if not config["files"]:
        print("[redact][x]: no files provided")
        return _callback.catch("", False)

    output_dir = Path("./data/redacted")
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_path in config["files"]:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            redacted = deepseek_redact(text, config["tags"])

            out_path = output_dir / Path(file_path).name
            out_path.write_text(redacted, encoding="utf-8")

            print(f"[redact][✓]: {Path(file_path).name} → {out_path.name}")

        except Exception as e:
            print(f"[redact][x]: {file_path} → {e}")

    return _callback.catch("", True)

command.add_func("redact", redact)

def download_emails(email_address, password, label, query, output_dir, limit):
    try:
        # Connect to the mail server (IMAP)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, "tukr nqjn ujnv ijby")  # Use the App Password here
        
        # Select mailbox folder (e.g., 'INBOX')
        mail.select(label)

        # Search for emails with the given query (e.g., "is:unread")
        status, messages = mail.search(None, query)
        email_ids = messages[0].split()

        # Limit the number of emails
        email_ids = email_ids[:limit]

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1], policy=policy.default)
                    subject, encoding = email.header.decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')

                    # Create a safe filename
                    filename = f"{hashlib.md5(subject.encode('utf-8')).hexdigest()}.eml"
                    filepath = Path(output_dir) / filename

                    # Write the email content to a file
                    with open(filepath, 'wb') as file:
                        file.write(response_part[1])

                    print(f"Saved: {filename} from {subject}")
    except Exception as e:
        print(f"Error while downloading emails: {e}")


# Main function to handle the `get` command logic
def get(PARAMS):
    config = {
        "email": None,
        "password": None,   # To store the app password
        "label": "INBOX",  # Default to 'INBOX' folder
        "query": "ALL",    # Default to 'ALL' emails
        "output": "./downloads",  # Default output folder
        "limit": 10        # Default limit of 10 emails
    }
    # Initialization function to parse flags and validate parameters
    def init(PARAMS):

        # If no parameters are passed, display the usage information
        if not PARAMS:
            usage.display(usage.get_usage("get"))
            return _callback.catch("", False), config

        # Parse the flags and assign values to the config
        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        for flag_token in flag_tokens:
            cleaned = flag_token.value.replace("-", "")
            index = util.indexOf(PARAMS, flag_token)

            if cleaned == "email":
                flag_contents = interface.extract_flags(PARAMS[index:])
                if flag_contents:
                    config["email"] = flag_contents[0].get_value()

            elif cleaned == "password":
                flag_contents = interface.extract_flags(PARAMS[index:])
                if flag_contents:
                    config["password"] = flag_contents[0].get_value()

            elif cleaned == "label":
                flag_contents = interface.extract_flags(PARAMS[index:])
                if flag_contents:
                    config["label"] = flag_contents[0].get_value()

            elif cleaned == "query":
                flag_contents = interface.extract_flags(PARAMS[index:])
                if flag_contents:
                    config["query"] = flag_contents[0].get_value()

            elif cleaned == "output":
                flag_contents = interface.extract_flags(PARAMS[index:])
                if flag_contents:
                    config["output"] = flag_contents[0].get_value()

            elif cleaned == "limit":
                flag_contents = interface.extract_flags(PARAMS[index:])
                print(PARAMS[index:])
                print(flag_contents)
                if flag_contents:
                    config["limit"] = int(flag_contents[0].get_value())

        if not config["email"]:
            print("[get][x]: Email address is required.")
            return _callback.catch("", False), config

        # Ensure the output directory exists
        Path(config["output"]).mkdir(parents=True, exist_ok=True)

        return _callback.catch("", True), config
    # Initialize command and parse parameters
    result, config = init(PARAMS)
    if not result.status:
        return result

    # Run the email download function
    print(type(config["limit"]))
    download_emails(config["email"], config["password"], config["label"], config["query"], config["output"], config["limit"])
    return _callback.catch(f"[get][✓]: Finished downloading {config['limit']} emails", True)

command.add_func("get", get)

def serialize_directories(directories):
    result = {}

    def walk(path):
        if path.is_file():
            return path.read_text(encoding="utf-8")
        elif path.is_dir():
            return {p.name: walk(p) for p in path.iterdir()}
        return None

    for directory in directories:
        root = Path(directory)
        if root.exists():
            result[root.name] = walk(root)

    return result


def deserialize_structure(structure: dict, root_folder: Path):
    def write(path: Path, content):
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            for key, value in content.items():
                write(path / key, value)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    for top, content in structure.items():
        write(root_folder / top, content)


def backup(PARAMS):
    config = {"name": None}

    def init():
        if not PARAMS:
            usage.display(usage.get_usage("backup"))
            return _callback.catch("", False)

        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        for flag_token in flag_tokens:
            cleaned = flag_token.value.replace("-", "")
            index = util.indexOf(PARAMS, flag_token)
            flag_contents = interface.extract_flags(PARAMS[index:])

            if cleaned == "name" and flag_contents:
                config["name"] = flag_contents[0].get_value()

        return _callback.catch("", True)

    result = init()
    if not result.status:
        return result

    name = config["name"] or datetime.now().strftime("backup_%Y%m%dT%H%M%S")
    backup_dir = Path("./data/memory/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    output_file = backup_dir / f"{name}.json"

    structure = serialize_directories(["data", "output"])

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2)

    print(f"[backup][✓]: saved backup of data/ and output/ to {output_file.name}")
    return _callback.catch("", True)


def restore(PARAMS):
    config = {"name": None}

    def init():
        if not PARAMS:
            usage.display(usage.get_usage("restore"))
            return _callback.catch("", False)

        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        for flag_token in flag_tokens:
            cleaned = flag_token.value.replace("-", "")
            index = util.indexOf(PARAMS, flag_token)
            flag_contents = interface.extract_flags(PARAMS[index:])

            if cleaned == "name" and flag_contents:
                config["name"] = flag_contents[0].get_value()

        return _callback.catch("", True)

    result = init()
    if not result.status:
        return result

    if not config["name"]:
        return _callback.catch("[restore][x]: please provide -name['<filename>.json']", False)


    backup_path = Path(f"./data/memory/backups{config["name"]}")
    if not backup_path.exists():
        return _callback.catch(f"[restore][x]: backup file {config['name']} not found", False)

    try:
        with open(backup_path, "r", encoding="utf-8") as f:
            structure = json.load(f)

        # Clear current directories before restoring
        for key in structure:
            restore_root = Path(key)
            if restore_root.exists():
                shutil.rmtree(restore_root)

        deserialize_structure(structure, Path("."))
        print(f"[restore][✓]: restored data and output folders from {config['name']}")
        return _callback.catch("", True)

    except Exception as e:
        return _callback.catch(f"[restore][x]: {str(e)}", False)



command.add_func("backup", backup)
command.add_func("restore", restore)

def run_highlight(PARAMS):
    # Handles: parse highlight -entities["person", "org"]
    pass



def run_templates(PARAMS):
    # Handles: parse templates -list, -create["name"], etc.
    pass

def help_command(PARAMS):
    print("[help][✓]: Available commands:")
    for name in command.get_body().keys():
        print(f"  - {name}")
    return _callback.catch("", True)

command.add_func("help", help_command)
command.add_func("h", help_command)

