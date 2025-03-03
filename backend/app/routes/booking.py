from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BookingRequest(BaseModel):
    guest_name: str
    check_in: str
    check_out: str
    guests: int
    breakfast: bool
    payment_method: str

@router.post("/")
def book_room(request: BookingRequest):
    """Handles hotel bookings."""
    confirmation_number = "ROOMIE-12345"
    return {"confirmation_number": confirmation_number}
