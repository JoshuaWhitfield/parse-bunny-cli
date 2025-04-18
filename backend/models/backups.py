# models/backups.py

from pydantic import BaseModel
from typing import Optional

class BackupPayload(BaseModel):
    organization: str
    cli_user_key: str
    backup_name: str
    encrypted_data: str  # Fernet-encrypted JSON string

class PullRequest(BaseModel):
    organization: str
    cli_user_key: str
    backup_name: str

class InternalLookupEntry(BaseModel):
    backup_name: str
    short_key: str
