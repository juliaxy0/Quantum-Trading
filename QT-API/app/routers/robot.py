from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
import uuid

from app.models.robot import Robot, RobotUpdate

robot = APIRouter()

@robot.post("/", response_description="Create a new robot", status_code=status.HTTP_201_CREATED, response_model=None)
def create_robot(request: Request, username: str, robot: Robot = Body(...)):
    robot = jsonable_encoder(robot)

    # Convert Quantity and Bought to numeric values
    robot["Quantity"] = float(robot["Quantity"])
    robot["Bought"] = float(robot["Bought"])

    # Check if the user exists
    user = request.app.database["users"].find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

    # Initialize the 'robots' field as an empty array if it doesn't exist yet
    if "robots" not in user:
        request.app.database["users"].update_one({"username": username}, {"$set": {"robots": []}})

    # Add the robot to the user's document
    request.app.database["users"].update_one({"username": username}, {"$push": {"robots": robot}})

    return None  # or any other response as needed

# @robot.get("/", response_description="List all robots for a user", response_model=List[Robot])
# def list_robots(request: Request, username: str):
#     robots = list(request.app.database["user"].find({"username": username}, limit=100))
#     return robots

# @robot.get("/{RobotName}", response_description="Get a single robot by RobotName", response_model=Robot)
# def find_robot(RobotName: str, request: Request, user_id: str):
#     if (robot := request.app.database["robot"].find_one({"RobotName": RobotName, "user_id": user_id})) is not None:
#         return robot
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {RobotName} not found for user {user_id}")

@robot.put("/{RobotName}", response_description="Update a robot", response_model=None)
def update_robot(RobotName: str, request: Request, username: str, robot_update: RobotUpdate = Body(...)):
    robot_update_dict = robot_update.dict(exclude_unset=True)

    # Check if there's anything to update
    if not robot_update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update parameters provided")

    # Perform the update using the positional operator $
    update_result = request.app.database["users"].update_one(
        {"username": username, "robots.RobotName": RobotName},
        {"$set": {"robots.$": robot_update_dict}}
    )

    # Check if the robot was found and updated
    if update_result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {RobotName} not found for username {username}")

    return None

@robot.delete("/{RobotName}", response_description="Delete a robot")
def delete_robot(RobotName: str, request: Request, response: Response, user_id: str):
    delete_result = request.app.database["robot"].delete_one({"RobotName": RobotName, "user_id": user_id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {RobotName} not found for user {user_id}")

