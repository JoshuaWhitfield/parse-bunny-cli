import hashlib
import random
from pydantic import BaseModel, EmailStr, Field

def generate_user_key() -> str:
    num = str(random.randint(10000000, 99999999))  # 8-digit number
    hash_prefix = hashlib.md5(num.encode()).hexdigest()[:8]
    return f"0x{hash_prefix}"

class User(BaseModel):
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    user_key: str = Field(default_factory=generate_user_key, description="User key")
