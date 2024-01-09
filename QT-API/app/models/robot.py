from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class Robot(BaseModel):
    RobotName: str = Field(...)
    Symbol: str = Field(...)
    Quantity: Decimal  = Field(...)
    Strategy: str = Field(...)
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
                "Status": "Running",
                "Bought": "0.01"
            }
        }

class RobotUpdate(BaseModel):
    Quantity: Optional[float]
    Stratergy: Optional[str]
    Status: Optional[str]

    class Config:
        arbitrary_types_allowed = True  # Add this line
        json_schema_extra = {
            "example": {
                "Quantity": 0.01,
                "Stratergy": "MACD",
                "Status": "Running",
            }
        }

class BoughtUpdate(BaseModel):
    Bought: float