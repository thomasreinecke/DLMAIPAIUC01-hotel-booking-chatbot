from pydantic import BaseModel, Field
from typing import Optional, Literal, TypedDict, List

class IntentClassification(BaseModel):
    """Classifies the user's intent."""
    intent: Literal["booking", "modify", "cancel", "confirm", "smalltalk"] = Field(
        ..., description="The classified intent of the user's message"
    )

class BookingInfo(BaseModel):
    """Stores booking-related information provided by the user."""
    full_name: Optional[str] = Field(None, description="The full name of the guest")
    check_in_date: Optional[str] = Field(None, description="Check-in date (YYYY-MM-DD)")
    check_out_date: Optional[str] = Field(None, description="Check-out date (YYYY-MM-DD)")
    num_guests: Optional[int] = Field(None, description="Number of guests")
    payment_method: Optional[str] = Field(None, description="Payment method")
    breakfast_included: Optional[bool] = Field(None, description="Whether breakfast is included")

class BookingState(TypedDict):
    """Tracks the booking state throughout the conversation."""
    intent: Optional[Literal["booking", "modify", "cancel", "confirm", "smalltalk"]]
    full_name: Optional[str]
    check_in_date: Optional[str]
    check_out_date: Optional[str]
    num_guests: Optional[int]
    payment_method: Optional[str]
    breakfast_included: Optional[bool]
    response: Optional[str]
