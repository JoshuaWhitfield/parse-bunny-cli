from pydantic import BaseModel

class OrganizationSignup(BaseModel):
    organization_name: str
    username: str
    password: str

class ShortKeyPayload(BaseModel):
    user_key: str
    fernet_short_key: str

class AddUserPayload(BaseModel):
    organization_name: str
    username: str
    password: str