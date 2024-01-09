from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
import uuid

from app.models.robot import Robot, RobotUpdate, BoughtUpdate 

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

@robot.put("/{RobotName}", response_description="Update a robot", response_model=None)
def update_robot(RobotName: str, request: Request, username: str, robot_update: RobotUpdate = Body(...)):
    robot_update_dict = robot_update.dict(exclude_unset=True)

    # Check if there's anything to update
    if not robot_update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update parameters provided")

    # Find the user by username
    user = request.app.database["users"].find_one({"username": username})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

    # Find the robot within the user's robots
    robots = user.get("robots", [])
    updated_robot = None

    for robot in robots:
        if robot["RobotName"] == RobotName:
            # Update only the specified attributes
            for key, value in robot_update_dict.items():
                robot[key] = value
            updated_robot = robot
            break

    # Check if the robot was found and updated
    if updated_robot:
        # Save the updated user document with the modified robots array
        request.app.database["users"].update_one({"username": username}, {"$set": {"robots": robots}})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {RobotName} not found for username {username}")

    return None

@robot.delete("/{RobotName}", response_description="Delete a robot", response_model=None)
def delete_robot(RobotName: str, request: Request, username: str):
    # Find the user by username
    user = request.app.database["users"].find_one({"username": username})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

    # Find the robot within the user's robots
    robots = user.get("robots", [])
    updated_robots = [robot for robot in robots if robot["RobotName"] != RobotName]

    # Check if the robot was found and deleted
    if len(robots) != len(updated_robots):
        # Save the updated user document with the modified robots array
        request.app.database["users"].update_one({"username": username}, {"$set": {"robots": updated_robots}})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {RobotName} not found for username {username}")

    return None

@robot.put("/{RobotName}/update_bought", response_description="Update the 'Bought' field of a robot", response_model=None)
def update_bought(RobotName: str, username: str, request: Request, new_bought_value: BoughtUpdate = Body(...)):
    # Find the user by username
    user = request.app.database["users"].find_one({"username": username})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

    # Find the robot within the user's robots
    robots = user.get("robots", [])
    updated_robot = None

    for robot in robots:
        if robot["RobotName"] == RobotName:
            # Update the 'Bought' field
            robot["Bought"] = new_bought_value.Bought  # Extract the value from the Pydantic model
            updated_robot = robot
            break

    # Check if the robot was found and updated
    if updated_robot:
        # Save the updated user document with the modified robots array
        request.app.database["users"].update_one({"username": username}, {"$set": {"robots": robots}})
        return True
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {RobotName} not found for username {username}")
