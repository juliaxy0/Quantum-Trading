import uuid
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId 
from decimal import Decimal

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    username: str = Field(...)
    password: str = Field(...)
    api_key: str = Field(...)
    secret_key: str = Field(...)

    class Config:
        arbitrary_types_allowed = True  # Add this line
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "username": "username",
                "password": "password",
                "api_key": "api_key",
                "secret_key": "secret_key"
            }
        }

class UserResponse(BaseModel):
    api_key: str
    secret_key: str
    
class UserUpdate(BaseModel):
    password: Optional[str]
    api_key: Optional[str]
    secret_key: Optional[str]

    class Config:
        arbitrary_types_allowed = True  # Add this line
        json_schema_extra = {
            "example": {
                "updated_password": "updated_password",
                "updated_api_key": "updated_api_key",
                "updated_secret_key": "updated_secret_key"
            }
        }

