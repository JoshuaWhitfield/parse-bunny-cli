# routes/backups.py

from fastapi import APIRouter, HTTPException
from models.backups import BackupPayload, PullRequest
from utils.mongo import db

router = APIRouter()

@router.post("/backups/push")
async def push_backup(payload: BackupPayload):
    """
    Stores the encrypted backup under organization → cli_user_key.
    Replaces backup if backup_name already exists.
    """
    result = db.backups.update_one(
        {
            "organization": payload.organization,
            "cli_user_key": payload.cli_user_key
        },
        {
            "$set": {
                f"backups.{payload.backup_name}": payload.encrypted_data
            }
        },
        upsert=True
    )

    return {"message": "Backup pushed successfully."}

@router.post("/backups/pull")
async def pull_backup(payload: PullRequest):
    """
    Retrieves the encrypted backup based on name under org + cli_user_key.
    """
    doc = db.backups.find_one({
        "organization": payload.organization,
        "cli_user_key": payload.cli_user_key
    })

    if not doc or "backups" not in doc:
        raise HTTPException(status_code=404, detail="No backups found for user.")

    encrypted_data = doc["backups"].get(payload.backup_name)
    if not encrypted_data:
        raise HTTPException(status_code=404, detail="Backup not found.")

    return {"encrypted_data": encrypted_data}
