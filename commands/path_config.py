from pathlib import Path

# Step 1: Define the centralized data path
def get_data_path():
    return Path("C:/parse-bunny/dashboard/data").resolve()

# Step 2: Preview updated paths for key operations
PATH = {
    "memory_backups": get_data_path() / "memory" / "backups",
    "classified": get_data_path() / "classified",
    "extracted": get_data_path() / "extracted",
    "templates": get_data_path() / "templates",
    "full_terms": get_data_path() / "templates" / "full_terms.json",
    "redacted": get_data_path() / "redact",
    "ingested": get_data_path() / "ingested",
    "search": get_data_path() / "search",
    "output": get_data_path() / "output",
    "downloads": get_data_path() / "downloads",
    "highlighted": get_data_path() / "highlighted"
}


Joshua Whitfield 3 minutes ago

Our project is going to consist of writing a fronted around a CLI chat bot. we are going to build a replit clone that allows us to show the file system (which our agent manipulates, on the left), the code editor (in the center), and two vertically split terminals. one to house the ai prompt, and the other to house the terminal for navigation and manipulation.
It is a harrowing project, but I already did 50% of it which is building the CLI/AI-shell framework that makes this work. I uploaded links to the repository in the Team's project information. definitely review that code before we start. This is a winning project and its already half way done by way of valid dependency rules.