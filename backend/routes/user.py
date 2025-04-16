from fastapi import APIRouter, HTTPException
from models.user import User, UserRegister, UserLookup  # adjust import if needed
from typing import List
from pymongo import MongoClient

users_db: List[User] = []  # in-memory database for demo

router = APIRouter()
client = MongoClient("mongodb://localhost:27017")
db = client["parsebunny"]
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

@router.post("/api/register")
async def register_user(data: UserRegister):
    existing = users_collection.find_one({"md5": data.md5})
    if existing:
        raise HTTPException(status_code=400, detail="User already registered.")

    users_collection.insert_one(data.dict())
    return {"status": "ok", "message": "User registered."}

@router.post("/api/lookup")
async def lookup_by_username(data: dict):
    user = users_collection.find_one({"username": data["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "md5": user["md5"],
        "short_key": user.get("short_key", None)
    }

