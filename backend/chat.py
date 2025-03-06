import os
import json
import logging
import random
import string
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

from local_llm import LMStudioLLM
from booking_chain import update_booking_state
from prompts import INIT_PROMPT, INTENT_IDENTIFICATION_PROMPT, RESET_PROMPT

load_dotenv()
router = APIRouter()
logging.basicConfig(level=logging.INFO)

with open("system-prompts.json", "r") as f:
    PROMPTS = json.load(f)

# In-memory stores for session state and chat history.
user_sessions = {}  # Maps sessionId -> state (a dict)
chat_history = {}   # Maps sessionId -> list of messages (each a dict with keys "text" and "sender")

class ChatRequest(BaseModel):
    message: str
    sessionId: str

llm = LMStudioLLM()

def transform_context(state: dict) -> dict:
    """
    Transforms the internal booking state into the context format expected by the frontend.
    """
    return {
        "intent": state.get("intent", "None"),
        "data": {
            "guest name": state.get("full_name") or None,
            "check-in date": state.get("check_in_date") or None,
            "check-out date": state.get("check_out_date") or None,
            "number of guests": state.get("num_guests") or None,
            "breakfast inclusion": state.get("breakfast_included") if state.get("breakfast_included") is not None else None,
            "payment method": state.get("payment_method") or None,
            "booking number": state.get("booking_number") or None
        }
    }

def identify_intent(user_input: str, session_id: str) -> str:
    """
    Uses the local LLM with a system prompt to determine the user's intent.
    Possible intents: booking, modify, cancel, confirm, reset, smalltalk.
    """
    prompt = f"{INTENT_IDENTIFICATION_PROMPT}\nUser: {user_input}"
    try:
        intent = llm.predict(prompt).strip().lower()
        if intent not in ["booking", "modify", "cancel", "confirm", "reset", "smalltalk"]:
            intent = "smalltalk"
        logging.info(f"[Session {session_id}] Identified intent: {intent}")
        return intent
    except Exception as e:
        logging.error(f"[Session {session_id}] Error in intent identification: {e}")
        return "smalltalk"

def query_llm(intent: str, user_message: str, session_id: str) -> str:
    """
    For non-booking intents, queries the local LLM using the corresponding system prompt.
    For reset, uses the RESET_PROMPT.
    """
    if intent == "reset":
        prompt = f"{RESET_PROMPT}\nUser: {user_message}"
    else:
        system_prompt = PROMPTS.get(intent, PROMPTS["smalltalk"])
        prompt = f"{system_prompt}\nUser: {user_message}"
    try:
        response = llm.predict(prompt)
        logging.info(f"[Session {session_id}] LLM response for intent '{intent}': {response}")
        return response
    except Exception as e:
        logging.error(f"[Session {session_id}] Error in LLM query for intent {intent}: {e}")
        return "I'm sorry, but I encountered an issue processing your request."

def generate_booking_number() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

def is_booking_complete(state: dict) -> bool:
    required = ["full_name", "check_in_date", "check_out_date", "num_guests", "payment_method", "breakfast_included"]
    for field in required:
        if not state.get(field):
            return False
    return True

@router.post("/")
def chat_endpoint(request: ChatRequest):
    session_id = request.sessionId
    user_message = request.message.strip()
    logging.info(f"[Session {session_id}] Received message: {user_message}")

    # Initialize session and chat history if not present.
    if session_id not in user_sessions:
        user_sessions[session_id] = {}
        chat_history[session_id] = []
        chat_history[session_id].append({"text": INIT_PROMPT, "sender": "bot"})
        logging.info(f"[Session {session_id}] New session. Sending init message.")
        return {"reply": INIT_PROMPT, "context": transform_context(user_sessions[session_id])}

    # Append user's message to chat history.
    chat_history[session_id].append({"text": user_message, "sender": "user"})

    # Build the full conversation history.
    conv_history = "\n".join(f"{msg['sender']}: {msg['text']}" for msg in chat_history[session_id])

    # Use LLM to identify intent.
    identified_intent = identify_intent(user_message, session_id)
    user_sessions[session_id]["intent"] = identified_intent

    # For modify, confirm, or cancel, if no booking number exists, treat as new booking.
    if identified_intent in ["modify", "cancel", "confirm"]:
        if not user_sessions[session_id].get("booking_number"):
            logging.info(f"[Session {session_id}] No booking number present; switching intent to booking.")
            identified_intent = "booking"
            user_sessions[session_id]["intent"] = "booking"

    if identified_intent == "reset":
        # Reset the session: clear state and history, then return the initial greeting.
        user_sessions[session_id] = {}
        chat_history[session_id] = []
        logging.info(f"[Session {session_id}] Conversation reset as per LLM intent.")
        return {"reply": INIT_PROMPT, "context": transform_context({}), "reset": True}

    if identified_intent == "booking":
        updated_state = update_booking_state(conv_history)
        logging.info("CHAIN OUTPUT (STATE): %s", updated_state)
        user_sessions[session_id].update(updated_state)
        bot_reply = updated_state.get("response", "Let's continue with your booking.")
        logging.info(f"[Session {session_id}] Updated booking state: {updated_state}")
        if is_booking_complete(user_sessions[session_id]):
            if not user_sessions[session_id].get("booking_number"):
                user_sessions[session_id]["booking_number"] = generate_booking_number()
            user_sessions[session_id]["booking_status"] = "confirmed"
            bot_reply = f"Thank you! Your booking is confirmed with booking number {user_sessions[session_id]['booking_number']}."
    else:
        bot_reply = query_llm(identified_intent, user_message, session_id)

    chat_history[session_id].append({"text": bot_reply, "sender": "bot"})
    return {"reply": bot_reply, "context": transform_context(user_sessions[session_id])}

@router.get("/history")
def get_chat_history(sessionId: str = None):
    if sessionId and sessionId in chat_history:
        return {"history": chat_history[sessionId]}
    else:
        return {"history": []}
