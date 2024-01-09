from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from typing import List
from bson import ObjectId

from app.models.user import User, UserResponse, UserUpdate

user = APIRouter()

@user.post("/login")
async def login(request: Request, user_info: dict = Body(...)):
    username = user_info.get("username")
    password = user_info.get("password")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid input")

    user_collection = request.app.database["users"]

    if (user := user_collection.find_one({"username": username})) is not None:
        if user["password"] == password:
            # Authentication successful
            return {"message": "Login successful", "authenticated": True, "_id": str(user["_id"])}

    # If the user is not found or the password doesn't match
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@user.get("/{id}", response_description="Get a single user by username", response_model=UserResponse)
def find_user(id: str, request: Request):
    try:
        id = ObjectId(id)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid user ID format")
    
    if (user := request.app.database["users"].find_one({"_id": id})) is not None:
        user_response = UserResponse(password=user.get('password'),username=user.get('username'), api_key=user.get('api_key'), secret_key=user.get('secret_key'))
        return user_response.dict()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")


@user.post("/create", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=None)
def create_user(request: Request, user: User = Body(...)):
    # Check if the username already exists
    existing_user = request.app.database["user"].find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    # If username doesn't exist, proceed to create the new user
    user_dict = jsonable_encoder(user)
    new_user = request.app.database["user"].insert_one(user_dict)
    return None

@user.get("/", response_description="List all users", response_model=List[User])
def list_users(request: Request):
    users = list(request.app.database["users"].find(limit=100))
    return users

@user.put("/{id}", response_description="Update a user", response_model=UserUpdate)
def update_user(id: str, request: Request, user_update: UserUpdate = Body(...)):
    try:
        user_id = ObjectId(id)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid user ID format")

    user_update = {k: v for k, v in user_update.dict().items() if v is not None}
    if len(user_update) >= 1:
        update_result = request.app.database["users"].update_one(
            {"_id": user_id}, {"$set": user_update}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

    if (existing_user := request.app.database["users"].find_one({"_id": user_id})) is not None:
        return existing_user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

