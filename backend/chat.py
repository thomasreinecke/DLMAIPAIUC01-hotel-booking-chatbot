import os
import json
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

from local_llm import LMStudioLLM
from booking_chain import update_booking_state
from models import BookingState, IntentClassification, BookingInfo
from prompts import BOOKING_STATE_PROMPT

load_dotenv()
router = APIRouter()
logging.basicConfig(level=logging.INFO)

with open("system-prompts.json", "r") as f:
    PROMPTS = json.load(f)

# In-memory stores for session state and chat history.
# user_sessions: maps sessionId -> state (a dict)
user_sessions = {}  
# chat_history: maps sessionId -> list of messages (each a dict with keys "text" and "sender")
chat_history = {}

class ChatRequest(BaseModel):
    message: str
    sessionId: str

llm = LMStudioLLM()

def transform_context(state: dict) -> dict:
    """
    Transforms our internal booking state into the context format expected by the frontend.
    Frontend expects a top-level "intent" and a "data" object with keys like "guest name", etc.
    """
    return {
        "intent": state.get("intent", "None"),
        "data": {
            "guest name": state.get("full_name") or "N/A",
            "check-in date": state.get("check_in_date") or "N/A",
            "check-out date": state.get("check_out_date") or "N/A",
            "number of guests": state.get("num_guests") or "N/A",
            "breakfast inclusion": state.get("breakfast_included") if state.get("breakfast_included") is not None else "N/A",
            "payment method": state.get("payment_method") or "N/A",
        }
    }

def identify_intent(user_input: str, session_id: str) -> str:
    """
    Uses the local LLM (with a system prompt) to determine the user's intent.
    Defaults to "smalltalk" if the returned intent is not recognized.
    """
    prompt = f"{PROMPTS['intent_identification']}\nUser: {user_input}"
    try:
        intent = llm.predict(prompt).strip().lower()
        if intent not in ["booking", "modify", "cancel", "confirm", "smalltalk"]:
            intent = "smalltalk"
        logging.info(f"[Session {session_id}] Identified intent: {intent}")
        return intent
    except Exception as e:
        logging.error(f"[Session {session_id}] Error in intent identification: {e}")
        return "smalltalk"

def query_llm(intent: str, user_message: str, session_id: str) -> str:
    """
    For non-booking intents, queries the local LLM using the corresponding system prompt.
    """
    system_prompt = PROMPTS.get(intent, PROMPTS["smalltalk"])
    prompt = f"{system_prompt}\nUser: {user_message}"
    try:
        response = llm.predict(prompt)
        logging.info(f"[Session {session_id}] LLM response for intent '{intent}': {response}")
        return response
    except Exception as e:
        logging.error(f"[Session {session_id}] Error in LLM query for intent {intent}: {e}")
        return "I'm sorry, but I encountered an issue processing your request."

@router.post("/")
def chat_endpoint(request: ChatRequest):
    session_id = request.sessionId
    user_message = request.message
    logging.info(f"[Session {session_id}] Received message: {user_message}")

    # Initialize session and chat history if not present.
    if session_id not in user_sessions:
        user_sessions[session_id] = {}  # Start with an empty state.
        chat_history[session_id] = []
        init_message = PROMPTS["init"]
        chat_history[session_id].append({"text": init_message, "sender": "bot"})
        logging.info(f"[Session {session_id}] New session. Sending init message.")
        return {"reply": init_message, "context": transform_context(user_sessions[session_id])}

    # Append the user's message to the session's chat history.
    chat_history[session_id].append({"text": user_message, "sender": "user"})

    # Build the full conversation history from all messages.
    conv_history = "\n".join(f"{msg['sender']}: {msg['text']}" for msg in chat_history[session_id])

    if user_sessions[session_id].get("intent") == "booking":
        updated_state = update_booking_state(conv_history)
        logging.info("CHAIN OUTPUT (STATE): %s", updated_state)
        user_sessions[session_id].update(updated_state)
        bot_reply = updated_state.get("response", "Let's continue with your booking.")
        logging.info(f"[Session {session_id}] Updated booking state: {updated_state}")
    else:
        identified_intent = identify_intent(user_message, session_id)
        user_sessions[session_id]["intent"] = identified_intent
        if identified_intent == "booking":
            updated_state = update_booking_state(conv_history)
            user_sessions[session_id].update(updated_state)
            bot_reply = updated_state.get("response", "Let's proceed with your booking.")
        else:
            bot_reply = query_llm(identified_intent, user_message, session_id)

    chat_history[session_id].append({"text": bot_reply, "sender": "bot"})
    return {"reply": bot_reply, "context": transform_context(user_sessions[session_id])}

@router.get("/history")
def get_chat_history(sessionId: str = None):
    """
    Returns the chat history for the given sessionId.
    If no sessionId is provided or the session does not exist, returns an empty array.
    """
    if sessionId and sessionId in chat_history:
        return {"history": chat_history[sessionId]}
    else:
        return {"history": []}
