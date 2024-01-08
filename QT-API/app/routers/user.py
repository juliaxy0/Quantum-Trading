from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
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
            return {"message": "Login successful", "authenticated": True}

    # If the user is not found or the password doesn't match
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@user.get("/{username}", response_description="Get a single user by username", response_model=UserResponse)
def find_user(username: str, request: Request):
    if (user := request.app.database["users"].find_one({"username": username})) is not None:
        user_response = UserResponse(api_key=user.get('api_key'), secret_key=user.get('secret_key'))
        return user_response.dict()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")


# @user.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User)
# def create_user(request: Request, user: User = Body(...)):
#     user = jsonable_encoder(user)
#     new_user = request.app.database["user"].insert_one(user)
#     created_user = request.app.database["user"].find_one({"_id": new_user.inserted_id})
#     return created_user

# @user.get("/", response_description="List all users", response_model=List[User])
# def list_users(request: Request):
#     users = list(request.app.database["user"].find(limit=100))
#     return users


# @user.put("/{username}", response_description="Update a user", response_model=User)
# def update_user(username: str, request: Request, user_update: UserUpdate = Body(...)):
#     user_update = {k: v for k, v in user_update.dict().items() if v is not None}
#     if len(user_update) >= 1:
#         update_result = request.app.database["user"].update_one(
#             {"username": username}, {"$set": user_update}
#         )

#         if update_result.modified_count == 0:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

#     if (existing_user := request.app.database["user"].find_one({"username": username})) is not None:
#         return existing_user

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

# @user.delete("/{username}", response_description="Delete a user")
# def delete_user(username: str, request: Request, response: Response):
#     delete_result = request.app.database["user"].delete_one({"username": username})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")
