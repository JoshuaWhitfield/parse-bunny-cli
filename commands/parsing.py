import importlib
import importlib.util
import json
import shutil
import os
import re
import hashlib
from datetime import datetime
from commands.command import command
from commands.path_config import PATH
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
from concurrent.futures import ThreadPoolExecutor, as_completed

def threaded(fn):
    def wrapper(file_paths, *args, **kwargs):
        results = []
        with ThreadPoolExecutor() as executor:
            future_to_path = {executor.submit(fn, path, *args, **kwargs): path for path in file_paths}
            for future in as_completed(future_to_path):
                result = future.result()
                if result:
                    results.append(result)
        return results
    return wrapper

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


from PyPDF2 import PdfReader
import docx
from PyPDF2 import PdfReader
import docx

def ingest_pdfs_from(path, out_folder):
    for file in Path(path).rglob("*.pdf"):
        try:
            reader = PdfReader(str(file))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

            if not text.strip():
                print(f"[ingest][x] PDF empty after parsing: {file}")
                continue

            md5 = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
            output_name = f"{Path(file).stem}_{md5}.txt"
            output_path = Path(out_folder) / output_name

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# Source: {file}\n")
                f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
                f.write(text.strip())

            print(f"[ingest][✓]: {output_name}")

        except Exception as e:
            print(f"[ingest][x] PDF failed: {file} → {e}")

def ingest_docx_from(path, out_folder):
    for file in Path(path).rglob("*.docx"):
        try:
            document = docx.Document(str(file))
            text = "\n".join(p.text for p in document.paragraphs)

            if not text.strip():
                print(f"[ingest][x] DOCX empty after parsing: {file}")
                continue

            md5 = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
            output_name = f"{Path(file).stem}_{md5}.txt"
            output_path = Path(out_folder) / output_name

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# Source: {file}\n")
                f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
                f.write(text.strip())

            print(f"[ingest][✓]: {output_name}")

        except Exception as e:
            print(f"[ingest][x] DOCX failed: {file} → {e}")

def ingest(PARAMS):
    config = {
        "pdf": [],
        "doc": [],
        "email": [],
        "output": Path(PATH["ingested"])
    }

    config["output"].mkdir(parents=True, exist_ok=True)

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

        if util.indexOf(["docx"], cleaned) > -1:
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

    output_path = PATH["classified"]
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"{config['name']}.json"

    def label_single_file(file_path):
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            label_data = deepseek_label(text)
            if label_data:
                print(f"[label][✓]: {Path(file_path).name} → {label_data['label']}")
                return {
                    "file": Path(file_path).name,
                    "label": label_data.get("label"),
                    "confidence": label_data.get("confidence"),
                    "model": "deepseek"
                }
        except Exception as e:
            print(f"[label][x]: error with {file_path} → {e}")
        return None

    # Use ThreadPoolExecutor with 15 threads
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(label_single_file, f) for f in config["files"]]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # Save results (no deduplication needed for label command)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    insert_log("label", {
        "params": [config["files"], config["name"]],
        "results": results
    })

    return _callback.catch(f"[label][✓]: saved to {output_file.name}", True)

command.add_func("label", label)

def deepseek_extract(text, clause_keys):
    import os
    import requests
    import json

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[extract][x]: missing OPENAI_API_KEY")
        print("please visit platform.deepseek.com/api_keys and create an api key")
        print("then copy it, and run in terminal:")
        print("> $env:OPENAI_API_KEY = 'YOUR_API_KEY'")
        return {}

    prompt = (
        "You are a legal clause extraction engine.\n"
        "Extract the following clauses from the text if they exist: "
        f"{', '.join(clause_keys)}\n\n"
        "Respond ONLY with a JSON object. For each clause, return:\n"
        "- `text`: the full sentence or paragraph\n"
        "- `line`: estimated line number in the text\n\n"
        "If a clause is not found, omit it from the result.\n"
        "Example:\n"
        "{\n"
        '  "confidentiality": {\n'
        '    "text": "This agreement is confidential...",\n'
        '    "line": 32\n'
        "  },\n"
        '  "termination_clause": {\n'
        '    "text": "Either party may terminate...",\n'
        '    "line": 54\n'
        "  }\n"
        "}\n\n"
        f"Text:\n{text[:3000]}"
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

    raw_content = response.json()["choices"][0]["message"]["content"]
    # print(f"\n[extract][debug]: Raw AI response:\n{raw_content}\n")
    cleaned = raw_content.strip().strip("```json").strip("```").strip()
    if not cleaned:
        return {}

    parsed = json.loads(cleaned)

    if response.status_code == 200:
        try:
            parsed = json.loads(response.json()["choices"][0]["message"]["content"])
            return parsed
        except Exception as e:
            print(f"[extract][x]: AI responded with invalid JSON → {e}")
            return {}
    else:
        print(f"[extract][x]: API error {response.status_code}")
        return {}

import re
import json
from pathlib import Path
from glob import glob

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
        flag_contents = interface.extract_flags(PARAMS[index:])

        if cleaned == "files":
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
            if flag_contents:
                config["template"] = flag_contents[0].get_value()

        elif cleaned == "name":
            if flag_contents:
                config["name"] = flag_contents[0].get_value()

    if not config["files"]:
        print("[extract][x]: no valid files provided.")
        return _callback.catch("", False)

    if not config["template"]:
        print("[extract][x]: missing -template[...] flag.")
        return _callback.catch("", False)

    # Load clause template
    template_file = normalize_path(f"./data/templates/{config['template']}.json")
    if not template_file.exists():
        print(f"[extract][x]: template not found → {template_file}")
        return _callback.catch("", False)

    with open(template_file, "r", encoding="utf-8") as f:
        template = json.load(f)

    results = []

    for file_path in config["files"]:
        try:
            text = Path(file_path).read_text(encoding="utf-8")

            # ✅ Optional: Strip HTML tags
            text = re.sub(r"<[^>]+>", "", text)

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
                            "line": i + 1,
                            "source": str(Path(file_path).resolve())  # ✅ Add source
                        }
                        break

            results.append({
                "file": Path(file_path).name,
                "extracted": extracted
            })

            print(f"[extract][✓]: {Path(file_path).name} → {len(extracted)} fields")

        except Exception as e:
            print(f"[extract][x]: error with {file_path} → {e}")

    # Save output
    output_dir = PATH["extracted"]
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = config["name"]
    out_file = output_dir / f"{output_name}.json"

    # Merge if file exists
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

    results = {}

    for file_path in config["files"]:
        try:
            content = Path(file_path).read_text(encoding="utf-8").strip()
            if not content:
                continue

            parsed_json = None
            try:
                parsed_json = json.loads(content)
            except json.JSONDecodeError:
                continue

            extract_hits = []
            if isinstance(parsed_json, list):
                extract_hits = parsed_json
            elif isinstance(parsed_json, dict):
                extract_hits = [parsed_json]

            for condition in config["extract"]:
                if "=" in condition:
                    key, val = map(str.strip, condition.split("=", 1))
                else:
                    key, val = condition.strip(), "*"

                for item in extract_hits:
                    extracted = item.get("extracted", {})
                    if not isinstance(extracted, dict):
                        continue

                    for clause_key, clause_val in extracted.items():
                        if clause_key == key and (val == "*" or val.lower() in clause_val.get("text", "").lower()):
                            match = dict(clause_val)
                            match["source"] = str(Path(file_path).resolve())
                            results.setdefault(key, []).append(match)

        except Exception as e:
            print(f"[search][x]: failed to parse {file_path} → {e}")

    # Save result
    search_dir = PATH["search"]
    search_dir.mkdir(parents=True, exist_ok=True)
    output_name = config["name"] or "results"
    output_file = search_dir / f"{output_name}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[search][✓]: found {sum(len(v) for v in results.values())} match(es). Saved to {output_file.name}")
    return _callback.catch("", True)


command.add_func("search", search)

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
    
# Existing redaction patterns
REDACT_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "ein": r"\b\d{2}-\d{7}\b",
    "id": r"\bID[-\s]?\d{3,10}\b",
    "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "date": r"\b(?:\d{1,2}[-/th|st|nd|rd\s]*)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[-\s]?\d{1,4}\b|\b\d{4}-\d{2}-\d{2}\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "zipcode": r"\b\d{5}(?:-\d{4})?\b",
    "state": r"\b(?:AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PA|PR|RI|SC|SD|TN|TX|UT|VT|VA|VI|WA|WV|WI|WY)\b",
    "passport": r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b",
    "drivers_license": r"\b[A-Z0-9]{1,9}\b",
    "bank_account": r"\b\d{9,18}\b",
    "routing_number": r"\b\d{9}\b",
    "address": r"\d{1,5}\s\w+(\s\w+){1,5},?\s(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr)\.?",
    "company": r"\b(?:Inc\.?|LLC|Ltd\.?|Corporation|Corp\.?)\b",
    "price": r"\$\d+(?:,\d{3})*(?:\.\d{2})?",
    "username": r"\b@[A-Za-z0-9_]+\b",
    "hashtag": r"\B#\w*[a-zA-Z]+\w*\b",
    "ipv6": r"\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "mac_address": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b",
    "hex_color": r"#(?:[0-9a-fA-F]{3}){1,2}",
    "uuid": r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
    "html_tag": r"</?[a-z][\s\S]*?>",
    "url": r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+",
    "password": r"\b(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}\b",
    "secret": r"\b(secret|confidential|private|restricted)\b",
    "eth_address": r"0x[a-fA-F0-9]{40}",
    "btc_address": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
    "language": r"\b(?:English|Spanish|French|German|Chinese|Arabic|Russian|Portuguese|Hindi|Japanese)\b",
    "country": r"\b(?:United States|Canada|Mexico|Brazil|China|India|Russia|Germany|France|UK)\b",
    "continent": r"\b(?:Africa|Asia|Europe|North America|South America|Australia|Antarctica)\b",
    "medical_term": r"\b(?:diabetes|cancer|asthma|arthritis|depression|stroke|fever|infection|virus|bacteria)\b",
    "drug": r"\b(?:aspirin|ibuprofen|acetaminophen|amoxicillin|penicillin|insulin|prozac|viagra|adderall|xanax)\b",
    "emotion": r"\b(?:happy|sad|angry|afraid|surprised|disgusted|joyful|depressed|anxious|calm)\b",
    "currency": r"\b(?:USD|EUR|GBP|JPY|CNY|INR|AUD|CAD|CHF|ZAR)\b",
    "gender": r"\b(?:male|female|nonbinary|transgender|cisgender|agender|genderqueer|bigender|androgyne|genderfluid)\b",
    "blood_type": r"\b(?:A|B|AB|O)[+-]\b",
    "temperature": r"\b\d{2,3}\s?(°C|°F)\b",
    "time": r"\b\d{1,2}:\d{2}(?:\s?[APap][Mm])?\b",
    "license_plate": r"\b[A-Z0-9]{1,7}\b",
    "social_media": r"\b(?:Facebook|Twitter|Instagram|LinkedIn|TikTok|Snapchat|Reddit|Pinterest|Tumblr|YouTube)\b",
    "education": r"\b(?:Bachelor|Master|PhD|High School|Diploma|GED|Associate|Degree)\b",
}

REDACT_PATTERNS_LIST = list(REDACT_PATTERNS.items())
REDACT_PATTERNS_LIST[:5]  # Show a preview


def redact(PARAMS):
    config = {
        "files": [],
        "tags": [],
        "ai": False
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
                if "*" in val:
                    config["files"] += [f for f in glob(val, recursive=True) if Path(f).is_file()]
                elif p.is_dir():
                    config["files"] += [str(f) for f in p.rglob("*.txt") if f.is_file()]
                elif p.is_file():
                    config["files"].append(str(p))

        elif cleaned == "tags":
            config["tags"] += [token.get_value().lower() for token in flag_contents]

        elif cleaned == "ai":
            config["ai"] = True

    if not config["files"]:
        print("[redact][x]: no files provided")
        return _callback.catch("", False)

    output_dir = Path("./data/redacted")
    output_dir.mkdir(parents=True, exist_ok=True)

    def process_file(file_path):
        try:
            text = Path(file_path).read_text(encoding="utf-8")

            if config["ai"]:
                redacted = deepseek_redact(text, config["tags"] or list(REDACT_PATTERNS.keys()))
            else:
                redacted = text
                for tag in (config["tags"] or REDACT_PATTERNS.keys()):
                    pattern = REDACT_PATTERNS.get(tag)
                    if pattern:
                        redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE)

            out_path = output_dir / Path(file_path).name
            out_path.write_text(redacted, encoding="utf-8")

            print(f"[redact][✓]: {Path(file_path).name} → redacted")
        except Exception as e:
            print(f"[redact][x]: {file_path} → {e}")

    with ThreadPoolExecutor(max_workers=23) as executor:
        executor.map(process_file, config["files"])

    return _callback.catch("[redact][✓]: All files redacted successfully", True)

command.add_func("redact", redact)

def download_emails(label, query, output_dir, limit):
    try:
        # 🔐 Load environment variables
        email_address = os.getenv("GGL_USER")
        password = os.getenv("GGL_PASS")

        if not email_address:
            print("[email][x]: missing $env:GGL_USER")
            return
        if not password:
            print("[email][x]: missing $env:GGL_PASS")
            return

        # Connect to the Gmail server (IMAP)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, password)

        # Select mailbox folder (e.g., 'INBOX')
        mail.select(label)

        # Search for emails with the given query (e.g., "ALL", "UNSEEN")
        status, messages = mail.search(None, query)
        email_ids = messages[0].split()

        # Limit number of emails
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
                    filepath = output_dir / filename

                    # Save the raw email content
                    with open(filepath, 'wb') as file:
                        file.write(response_part[1])

                    print(f"Saved: {filename} from {subject}")
    except Exception as e:
        print(f"Error while downloading emails: {e}")

# Main function to handle the `get` command logic
def get(PARAMS):
    config = {
        "email": os.getenv("GGL_USER"),
        "password": os.getenv("GGL_PASS"),
        "label": "INBOX",
        "query": "ALL",
        "output": Path(PATH["downloads"]),  # set default as Path
        "limit": 10
    }

    def init(PARAMS):
        if not PARAMS:
            usage.display(usage.get_usage("get"))
            return _callback.catch("", False), config

        flag_tokens = interface.extract(PARAMS, [TT.Flag()])
        for flag_token in flag_tokens:
            cleaned = flag_token.value.replace("-", "")
            index = util.indexOf(PARAMS, flag_token)
            flag_contents = interface.extract_flags(PARAMS[index:])

            if cleaned == "email":
                if flag_contents:
                    config["email"] = flag_contents[0].get_value()

            elif cleaned == "password":
                if flag_contents:
                    config["password"] = flag_contents[0].get_value()

            elif cleaned == "label":
                if flag_contents:
                    config["label"] = flag_contents[0].get_value()

            elif cleaned == "query":
                if flag_contents:
                    config["query"] = flag_contents[0].get_value()

            elif cleaned == "output":
                if flag_contents:
                    config["output"] = Path(flag_contents[0].get_value()).resolve()

            elif cleaned == "limit":
                if flag_contents:
                    config["limit"] = int(flag_contents[0].get_value())

        # Ensure output path exists
        config["output"].mkdir(parents=True, exist_ok=True)

        # Validate required fields
        if not config["email"]:
            print("[get][x]: missing $env:GGL_USER or -email[...]")
            return _callback.catch("", False), config

        if not config["password"]:
            print("[get][x]: missing $env:GGL_PASS or -password[...]")
            return _callback.catch("", False), config

        return _callback.catch("", True), config

    result, config = init(PARAMS)
    if not result.status:
        return result

    # Run download
    download_emails(
        label=config["label"],
        query=config["query"],
        output_dir=config["output"],
        limit=config["limit"]
    )

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
    backup_dir = PATH["memory_backups"]
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


    backup_path = PATH["memory_backups"] / f"{config["name"]}.json"
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

