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
usage.add_usage("ingest", [" ingest -pdf['</path/to>', ...] -output['</path/to>']", " ingest -email['</path/to>', ...] -doc['</path/to>']"], "This command ingests PDF, DOCX, and EML files from the specified paths, extracts raw text, and stores it into the output directory for downstream classification, extraction, and search.", "db", "")
usage.add_usage("db", [" db -show <table_name> "], "this command displays the contents stored in the database powered by Memurai.", "db", "")
usage.add_usage(
    "label",
    [
        " label -files['</path/to/file.txt>', ...] -name['<output_name>']"
    ],
    "Automatically labels text documents using the DeepSeek API. The results are saved as data/classified/<name>.json, "
    "where each entry contains file name, predicted label, confidence score, and model source.",
    "label",
    ""
)
usage.add_usage(
    "extract",
    [
        " extract -files['</path/to/*.txt>'] -template['<template_name>'] -name['<output_name>']"
    ],
    "Extracts legal clauses from text files using a named clause template. "
    "Results are saved to data/extracted/<name>.json. If -name is not provided, the template name is used by default.",
    "extract",
    ""
)
usage.add_usage(
    "search",
    [
        " search -files['</path/to/dir/or/file>'] -label['nda']",
        " search -files['</path/to/*.json>'] -extract['jurisdiction=california']",
        " search -files['</path/to/*.txt>'] -text['confidentiality'] -name['confidential_hits']"
    ],
    "Searches classified, extracted, or raw text data using flags. Results are saved to data/search/<name>.json. If -name[...] is not provided, defaults to 'results.json'. Supports matching on -label, -extract, and -text.",
    "search",
    ""
)

usage.add_usage(
    "redact",
    [
        " redact -files['</path/*.txt>'] -tags['email', 'ssn', 'date', 'ip'] "
    ],
    "Redacts sensitive patterns like emails, SSNs, IPs, and dates from .txt files. Outputs redacted files to data/redacted/.",
    "ai",
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
