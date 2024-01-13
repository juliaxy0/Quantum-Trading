from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class Robot(BaseModel):
    RobotName: str = Field(...)
    Symbol: str = Field(...)
    Quantity: Decimal  = Field(...)
    Strategy: str = Field(...)
    Sentiment : bool = Field(...)
    Prediction : bool = Field(...)
    Status: str = Field(...)
    Bought: Decimal  = Field(...)

    class Config:
        arbitrary_types_allowed = True  # Add this line
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "RobotName": "Robot1",
                "Symbol": "Miguel de Cervantes",
                "Quantity": "0.01",
                "Strategy": "MACD",
                "Sentiment" : True,
                "Prediction" : True,
                "Status": "Running",
                "Bought": "0.01"
            }
        }

class RobotUpdate(BaseModel):
    Quantity: Optional[float]
    Strategy: Optional[str]
    Sentiment:Optional[bool]
    Prediction:Optional[bool]
    Status: Optional[str]

    class Config:
        arbitrary_types_allowed = True  # Add this line
        json_schema_extra = {
            "example": {
                "Quantity": 0.01,
                "Strategy": "MACD",
                "Status": "Running",
                "Sentiment" : True,
                "Prediction" : True,
            }
        }

class BoughtUpdate(BaseModel):
    Bought: float