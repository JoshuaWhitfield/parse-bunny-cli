from fastapi import APIRouter, HTTPException
from models.user import User, UserRegister, UserLookup  # adjust import if needed
from typing import List
from pymongo import MongoClient

users_db: List[User] = []  # in-memory database for demo

router = APIRouter()
client = MongoClient("mongodb://localhost:27017")
db = client["parsebunny"]
organizations_collection = db["organizations"]
users_collection = db["users"]

@router.post("/users")
def create_user(user: User):
    user_dict = user.dict()
    result = users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)  # convert ObjectId to string
    return user_dict
@router.get("/users")
def get_users():
    return users_db
@router.get("/verify/{user_key}")
def verify_license(user_key: str):
    user = users_collection.find_one({"user_key": user_key})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.get("paid", False):
        raise HTTPException(status_code=402, detail="Payment required")
    return {"status": "verified"}

@router.post("/api/org/signup")
async def signup_organization(data: dict):
    org_name = data.get("organization_name")
    username = data.get("username")
    password = data.get("password")

    if not org_name or not username or not password:
        raise HTTPException(status_code=400, detail="Missing fields")

    # Check if org exists already
    exists = organizations_collection.find_one({"organization_name": org_name})
    if exists:
        return {"status": "ok", "message": "Organization already exists"}

    # Insert new org
    organizations_collection.insert_one({
        "organization_name": org_name,
        "created_by": username,
        "users": [
            {
                "username": username,
                "password": password
            }
        ]
    })

    return {"status": "ok", "message": "Organization created"}
@router.post("/api/lookup")
async def lookup_by_username(data: dict):
    user = users_collection.find_one({"username": data["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "md5": user["md5"],
        "short_key": user.get("short_key", None)
    }

