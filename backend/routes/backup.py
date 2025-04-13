from fastapi import APIRouter
from models.backup_model import BackupModel
from utils.mongo import db

router = APIRouter()

@router.post("/backup")
def save_backup(backup: BackupModel):
    db.backups.insert_one(backup.dict())
    return {"message": "Backup saved"}

@router.get("/backups")
def list_backups():
    return list(db.backups.find({}, {"_id": 0}))
