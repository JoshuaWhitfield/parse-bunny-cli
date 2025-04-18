from fastapi import APIRouter, HTTPException, Query
from models.organization import OrganizationSignup, ShortKeyPayload
from utils.mongo import db
import hashlib
from datetime import datetime

router = APIRouter()

@router.post("/org/signup")
async def signup_org(payload: OrganizationSignup):
    password_md5 = hashlib.md5(payload.password.encode()).hexdigest()
    user_key = hashlib.md5(payload.username.encode()).hexdigest()

    new_org = {
        "organization_name": payload.organization_name,
        "data_created": datetime.utcnow(),
        "cli_user_list": [
            {
                "username": payload.username,
                "password": password_md5,
                "user_key": user_key,
                "backups": []
            }
        ]
    }

    existing = db.organizations.find_one({
        "organization_name": payload.organization_name,
        "cli_user_list.username": payload.username
    })

    if existing:
        raise HTTPException(status_code=400, detail="Organization or user already exists")

    result = db.organizations.insert_one(new_org)
    return {"message": "Organization created", "id": str(result.inserted_id)}

@router.get("/org/lookup-key")
async def lookup_short_key(username: str = Query(...), organization: str = Query(...)):
    org = db.organizations.find_one({"organization_name": organization})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = next((u for u in org["cli_user_list"] if u["username"] == username), None)
    if not user or "fernet_short_key" not in user:
        raise HTTPException(status_code=404, detail="fernet_short_key not found")

    return {"fernet_short_key": user["fernet_short_key"]}


@router.patch("/org/update-key")
async def update_short_key(payload: ShortKeyPayload):
    result = db.organizations.update_one(
        {"cli_user_list.user_key": payload.user_key},
        {"$set": {"cli_user_list.$.fernet_short_key": payload.fernet_short_key}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User key not found")

    return {"message": "Short key updated successfully"}

@router.get("/org/lookup")
async def lookup_org_user(
    username: str = Query(...),
    organization: str = Query(...)
):
    """
    Lookup if an organization exists and whether the username exists within it.
    """
    org = db.organizations.find_one({"organization_name": organization})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user = next((user for user in org.get("cli_user_list", []) if user["username"] == username), None)

    return {
        "organization_exists": True,
        "user_exists": user is not None
    }

from models.organization import AddUserPayload

@router.post("/org/add_user")
async def add_user_to_existing_org(payload: AddUserPayload):
    org = db.organizations.find_one({"organization_name": payload.organization_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    existing_user = next((u for u in org.get("cli_user_list", []) if u["username"] == payload.username), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists in organization")

    password_md5 = hashlib.md5(payload.password.encode()).hexdigest()
    user_key = hashlib.md5(payload.username.encode()).hexdigest()

    result = db.organizations.update_one(
        {"organization_name": payload.organization_name},
        {"$push": {
            "cli_user_list": {
                "username": payload.username,
                "password": password_md5,
                "user_key": user_key,
                "backups": []
            }
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add user")

    return {"message": "User added to organization"}
