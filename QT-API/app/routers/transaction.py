from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder

from app.models.transaction import Transaction

transaction = APIRouter()

@transaction.post("/", response_description="Create a new transaction", status_code=status.HTTP_201_CREATED, response_model=None)
def create_transaction(request: Request, username: str, robotName: str, transaction: Transaction = Body(...)):
    transaction = jsonable_encoder(transaction)

    # Find the user by username
    user = request.app.database["users"].find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")

    # Find the robot within the user's robots
    robots = user.get("robots", [])
    selected_robot = None

    for robot in robots:
        if robot["RobotName"] == robotName:
            selected_robot = robot
            break

    if selected_robot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Robot with RobotName {robotName} not found for username {username}")

    # Initialize the 'transactions' field as an empty array if it doesn't exist yet
    if "transactions" not in selected_robot:
        selected_robot["transactions"] = []

    # Add the transaction to the robot's document
    selected_robot["transactions"].append(transaction)

    # Save the updated user document with the modified robots array
    request.app.database["users"].update_one({"username": username}, {"$set": {"robots": robots}})

    return None  # or any other response as needed
