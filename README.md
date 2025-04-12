# parse-bunny-cli
This is a data parsing and redaction CLI for AI model training, legal document analysis, and sensitive data workflows.

<h1>Getting Started:</h1>
<p>Clone the repository and install the following dependencies:</p>

```bash
$ git clone https://github.com/JoshuaWhitfield/parse-bunny-cli.git
$ cd parse-bunny-cli

$ python3 -m venv parse-bunny
$ parse-bunny\Scripts\activate  # (or `source parse-bunny/bin/activate` on Unix)

$ python3 -m pip install -r requirements.txt

# Then run the CLI
$ python3 main.py
```

<h1>Commands:</h1>

<h3>clear</h3>
<h4>description:</h4>
<p>Clears the terminal screen.</p>

<h3>reset</h3>
<h4>description:</h4>
<p>Clears the contents of the 'data' output directory.</p>

<h3>data</h3>
<h4>usage:</h4>

```bash
$ data -collect["<keyword>"]
$ data -collect["<keyword>"] -parse["/path/to/parser.py"]
$ data -collect["<keyword>"] -parse[]  # use default parser
```

<h4>description:</h4>
<p>Collects web content by keyword and optionally parses it with a custom or built-in parser.</p>

```python
class Parser:
    def __init__(self):
        self.input = ""
        self.output = ""

    def set_input(self, new_input):
        self.input = new_input

    def get_output(self):
        return self.output

    def parse(self):
        # your parsing logic

# Required entry point for custom parser:
def run_parser(input):
    parser = Parser()
    parser.set_input(input)
    parser.parse()
    return parser.get_output()
```

<h3>ingest</h3>
<h4>usage:</h4>

```bash
$ ingest -pdf["/path/to/folder"] -output["/path/to/output"]
$ ingest -doc["/path/to/docs"]
$ ingest -email["/path/to/emls"]
```

<h4>description:</h4>
<p>Extracts text from PDF, DOCX, and EML files and outputs plaintext `.txt` files to the ingested directory.</p>

<h3>label</h3>
<h4>usage:</h4>

```bash
$ label -files["/data/ingested/*.txt"] -name["classified_batch"]
```

<h4>description:</h4>
<p>Automatically classifies ingested text files using DeepSeek. Outputs JSON files to `data/classified/`.</p>

<h3>extract</h3>
<h4>usage:</h4>

```bash
$ extract -files["/data/ingested/*.txt"] -template["full_terms"] -name["contract_terms"]
```

<h4>description:</h4>
<p>Extracts predefined legal clauses like `payment_terms`, `jurisdiction`, `confidentiality`, etc., using regex templates. Outputs JSON to `data/extracted/`.</p>

<h3>search</h3>
<h4>usage:</h4>

```bash
$ search -files["/data/extracted"] -extract["jurisdiction=california"] -name["ca_jurisdiction"]
```

<h4>description:</h4>
<p>Searches extracted or classified data for label, text, or field matches. Outputs results to `data/search/<name>.json`.</p>

<h3>redact</h3>
<h4>usage:</h4>

```bash
$ redact -files["/data/ingested/*.txt"]
```

<h4>description:</h4>
<p>Uses DeepSeek LLM to automatically redact names, timestamps, and sensitive fields. Saves output to `data/redacted/`.</p>

<h1>Inputs</h1>

<h3>↑ up arrow key</h3>
<h4>description:</h4>
<p>Recall previous command in terminal for reuse.</p>

<h4>Exit the CLI:</h4>
<p>Press <code>CTRL + C</code> or type <code>exit</code>.</p>
