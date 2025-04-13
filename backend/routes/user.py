from fastapi import APIRouter, HTTPException
from models.user import User  # adjust import if needed
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