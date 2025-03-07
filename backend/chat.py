import os
import json
import logging
import random
import string
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

from local_llm import LMStudioLLM
from booking_chain import update_booking_context
from prompts import INIT_PROMPT
from database import init_db, upsert_booking  # <--- import the DB methods

load_dotenv()
router = APIRouter()
logging.basicConfig(level=logging.INFO)

with open("system-prompts.json", "r") as f:
    PROMPTS = json.load(f)

# In-memory stores for booking context and chat history.
booking_contexts = {}
chat_history = {}

class ChatRequest(BaseModel):
    message: str
    sessionId: str

llm = LMStudioLLM()

def transform_context(state: dict) -> dict:
    return {
        "intent": state.get("last_intent", "None"),
        "status": state.get("status", "draft"),
        "data": {
            "guest name": state.get("full_name") or None,
            "check-in date": state.get("check_in_date") or None,
            "check-out date": state.get("check_out_date") or None,
            "number of guests": state.get("num_guests") or None,
            "breakfast inclusion": state.get("breakfast_included") or None,
            "payment method": state.get("payment_method") or None,
            "booking number": state.get("booking_number") or None,
            "language": state.get("language") or "English"
        }
    }

def generate_booking_number() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

# Initialize the database at startup (e.g., using FastAPI's startup event or here at module level)
init_db()

@router.post("/")
def chat_endpoint(request: ChatRequest):
    session_id = request.sessionId
    user_message = request.message.strip()
    logging.info(f"[Session {session_id}] Received message: {user_message}")

    # Initialize session if not present.
    if session_id not in booking_contexts:
        booking_contexts[session_id] = {}
        chat_history[session_id] = []
        chat_history[session_id].append({"text": INIT_PROMPT, "sender": "bot"})
        logging.info(f"[Session {session_id}] New session. Sending init message.")
        return {"reply": INIT_PROMPT, "context": transform_context(booking_contexts[session_id])}

    # Append user's message to chat history
    chat_history[session_id].append({"text": user_message, "sender": "user"})

    # Build the full conversation history
    conv_history = "\n".join(f"{msg['sender']}: {msg['text']}" for msg in chat_history[session_id])

    # Update booking context via the LLM chain
    updated_context = update_booking_context(conv_history, booking_contexts[session_id], user_message)
    logging.info(f"[Session {session_id}] Updated booking context: {updated_context}")

    # If the LLM indicates reset, clear session
    if updated_context.get("last_intent") == "reset":
        booking_contexts[session_id] = {}
        chat_history[session_id] = []
        logging.info(f"[Session {session_id}] Reset intent detected. Clearing session.")
        return {"reply": INIT_PROMPT, "context": transform_context({}), "reset": True}

    # If the stored context was already confirmed, preserve booking_number and status
    if booking_contexts[session_id].get("status") == "confirmed":
        updated_context["status"] = "confirmed"
        updated_context["booking_number"] = booking_contexts[session_id].get("booking_number")

    # Overwrite with new context
    booking_contexts[session_id] = updated_context

    # If context is "confirmed", ensure booking_number is set, then upsert
    if updated_context.get("status") == "confirmed":
        if not updated_context.get("booking_number"):
            updated_context["booking_number"] = generate_booking_number()
        # Persist to DB
        upsert_booking(updated_context)
        bot_reply = updated_context.get("response", "Your booking is confirmed.")
    else:
        bot_reply = updated_context.get("response", "I'm here to help you with your booking.")

    # Append the bot's reply to chat history
    chat_history[session_id].append({"text": bot_reply, "sender": "bot"})

    return {"reply": bot_reply, "context": transform_context(updated_context)}

@router.get("/history")
def get_chat_history(sessionId: str = None):
    if sessionId and sessionId in chat_history:
        return {"history": chat_history[sessionId]}
    else:
        return {"history": []}
