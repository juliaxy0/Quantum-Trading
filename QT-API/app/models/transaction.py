from pydantic import BaseModel, Field
from decimal import Decimal

class Transaction(BaseModel):
    time: str = Field(...)
    transaction_id: str = Field(...)
    quantity: Decimal = Field(...)
    filled_price: Decimal = Field(...)
    type: str = Field(...)

    class Config:
        arbitrary_types_allowed = True  # Add this line
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "time": "2022-01-01T00:00:00",
                "transaction_id": "123",
                "quantity": 0.01,
                "filled_price": 5000.0,
                "type": "Buy"
            }
        }