from fastapi import APIRouter
from pydantic import BaseModel
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

# Store chat history in memory for now
chat_history = []

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def chat(request: ChatRequest):
    """Handles user messages."""
    logging.info(f"User: {request.message}")

    # Simulated bot response
    bot_reply = "I'm Roomie! I can help with your hotel booking."

    # Store messages
    chat_history.append({"text": request.message, "sender": "user"})
    chat_history.append({"text": bot_reply, "sender": "bot"})

    logging.info(f"Bot: {bot_reply}")
    return {"reply": bot_reply}

@router.get("/history")
def get_chat_history():
    """Fetch previous chat messages."""
    return {"history": chat_history}
