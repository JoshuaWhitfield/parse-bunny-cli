from internal.usage_object import UsageObject

class Usage:
    def __init__(self):
        self.body = {}

    def add_usage(self, cmd_name, usage_array, description, long, short):
        usage_object = UsageObject(cmd_name, usage_array, description, long, short)
        self.body[cmd_name] = usage_object
        return usage_object
    
    def get_usage(self, cmd_name):
        if cmd_name not in self.body:
            return None
        return self.body[cmd_name]
    
    def display(self, usage_object):
        # Fixing the join() issue for usage_array
        print("COMMAND: " + usage_object.get_name().upper())
        print(" " + "\n ".join(usage_object.get_usage_array()))  # Correct usage of join
        print(" desc: " + usage_object.get_description())
        print(" long: " + usage_object.get_long())
        if usage_object.get_short() != "":
            print(" short: " + usage_object.get_short())
        return True

# Example usage
usage = Usage()

usage.add_usage("clear", [" clear ", " cls "], "this command clears the terminal.", " clear ", " cls ")
usage.add_usage("data", [" data -collect['<string_keyword>', ...] ", " data -collect['<string_keyword>', ...] -parse['/full/path/to/parser'] ", " data -collect['<keywords>'] -parse[] "], "this command can collect and parse information for AI model training. by ommitting the path from the -parse flag, you use the built in parser.", " data ", "")
usage.add_usage("ingest", [" ingest -pdf['</path/to/dir>', ...] -output['</path/to/dir>']", " ingest -email['</path/to/dir>', ...] -docx['</path/to/dir>']"], "This command ingests PDF, DOCX, and EML files from the specified paths, extracts raw text, and stores it into the output directory for downstream classification, extraction, and search.", " ingest ", "")
usage.add_usage(
    "label",
    [
        " label -files['</path/to/file.txt>', '</path/to/dir>' ...] -name['<output_name>']"
    ],
    "Automatically labels text documents using the DeepSeek API. The results are saved as data/classified/<name>.json, "
    "where each entry contains file name, predicted label, confidence score, and model source.",
    "label",
    ""
)
usage.add_usage(
    "extract",
    [
        " extract -files['</path/to/dir/*.txt>', </path/to/dir>, ...] -name['<output_name>']"
    ],
    "Extracts legal clauses from text files using a named clause template. "
    "Results are saved to data/extracted/<name>.json. If -name is not provided, the template name is used by default.",
    "extract",
    ""
)
usage.add_usage(
    "search",
    [
        " search -files['</path/to/*.json>'] -extract['<term>']",
    ],
    "Searches classified, extracted, or raw text data using flags. Uses terms from '/templates/full_terms.json' (see documentation for terms). Results are saved to data/search/<name>.json. If -name[...] is not provided, defaults to 'results.json'. Supports matching on -label, -extract, and -text.",
    "search",
    ""
)
usage.add_usage(
    "redact",
    [
        " redact -files['</path/*.txt>', </path/to/dir>, ...] -tags['email', 'ssn', 'date', 'ip', '<arbitrary>'] "
    ],
    "Redacts sensitive patterns like emails, SSNs, IPs, and dates from .txt files. Outputs redacted files to data/redacted/. tags go directly into the ai prompt, so be specific.",
    "redact",
    ""
)
usage.add_usage(
    "get",
    [
        " get -output['</path/to/dir>'] -limit[10]",
        " get -limit[5]"
    ],
    "Download emails from a specified email address and label (folder) with optional query and limit. Saves the emails as .eml files in the specified output directory.",
    "get",
    ""
)

usage.add_usage(
    "highlight",
    [
        " highlight -files['</path/to/*.txt>'] -regex['<term1>', '<term2>'] -ai['<clause1>', '<clause2>']",
    ],
    "Generates highlighted PDFs based on detected matches. Highlights both predefined regex terms and AI-identified legal clauses. Outputs to 'C:/parse-bunny/dashboard/data/highlighted/'. Use -regex[...] for keyword matching and -ai[...] to include AI clause detection.",
    "highlight",
    ""
)

usage.add_usage(
    "reset",
    [
        " reset -all",
        " reset -data",
        " reset -downloads",
        " reset -ingest",
        " reset -search",
        " reset -extract",
        " reset -label",
        " reset -highlight",
        " reset -redact"
    ],
    "Resets selected directories by clearing their contents. Use flags to control which folders are cleared. Use -all to wipe everything inside the 'data' and 'downloads' directories. No files are deleted permanently—only emptied from Parse Bunny directories.",
    "reset",
    ""
)



usage.add_usage("backup", [
    " backup -name['<optional_filename>'] "
], "Backs up memory.json to data/memory/backups/ with optional name", "meta", "")

usage.add_usage("restore", [
    " restore -name['<filename>'] "
], "Restores memory.json from a specified backup file in backups/", "meta", "")




# usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")
# usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")
# usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")
# usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")
# usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")

# Test displaying usage
