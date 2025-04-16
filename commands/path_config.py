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
