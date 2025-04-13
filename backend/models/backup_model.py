from pydantic import BaseModel
from typing import List, Optional

class RedactedContent(BaseModel):
    source: str
    content: str
    changes: Optional[str] = None

class BackupModel(BaseModel):
    name: str
    created_at: str
    data: List[RedactedContent]
