import os
import json
import logging
import random
import string
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

from llm import LMStudioLLM
from chain import update_booking_context
from prompts import INIT_PROMPT
from database import init_db, upsert_booking, get_booking_by_number_and_name

load_dotenv()
router = APIRouter()
logging.basicConfig(level=logging.INFO)

# In-memory stores for booking context and chat history.
booking_contexts = {}  # Maps sessionId -> booking context (a dict)
chat_history = {}      # Maps sessionId -> list of messages (each dict with "text" and "sender")

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

def is_booking_complete(state: dict) -> bool:
    """
    Checks whether all required booking fields are populated.
    Logs populated fields, missing fields, and overall completeness.
    """
    required = ["full_name", "check_in_date", "check_out_date", "num_guests", "payment_method", "breakfast_included"]
    populated = []
    missing = []

    for field in required:
        if state.get(field):
            populated.append(field)
        else:
            missing.append(field)

    is_complete = len(missing) == 0

    logging.info(f"Booking context completeness check:")
    logging.info(f"  ✅ Populated fields: {populated}")
    logging.info(f"  ❌ Missing fields: {missing}")
    logging.info(f"  🧮 isComplete: {is_complete}")

    return is_complete


def rectify_context(session_id: str, state: dict) -> dict:
    """
    Validates and adjusts booking context:
    - Ensures valid intent and status
    - Downgrades incomplete confirmed/pending to draft
    - Prompts for name/number if required
    """
    # Validate intent
    valid_intents = {"book", "modify", "cancel", "reset", "smalltalk"}
    intent = state.get("last_intent")
    if intent not in valid_intents:
        logging.warning(f"[Session {session_id}] Invalid intent '{intent}' replaced with 'smalltalk'")
        state["last_intent"] = "smalltalk"
        intent = "smalltalk"

    # Validate status
    valid_statuses = {"draft", "pending", "confirmed"}
    status = state.get("status")
    if status not in valid_statuses:
        logging.warning(f"[Session {session_id}] Invalid status '{status}' replaced with 'draft'")
        state["status"] = "draft"
        status = "draft"

    booking_number = state.get("booking_number")
    full_name = state.get("full_name")
    print(f"FOUND booking_number={booking_number} | full_name={full_name}")

    # Request identity for modify/cancel
    if intent in ["modify", "cancel"] and (not full_name or not booking_number):
        state["response"] = "To proceed with your request, please provide your full name and reservation number."
        if chat_history.get(session_id) and chat_history[session_id][-1]["sender"] == "bot":
            chat_history[session_id].pop()
        chat_history[session_id].append({"text": state["response"], "sender": "bot"})
        return state

    # Rectify confirmed/pending with incomplete data
    if status in ["pending", "confirmed"] and not is_booking_complete(state):
        logging.info(f"[Session {session_id}] Rectifying incomplete booking (was '{status}')")
        state["status"] = "draft"
        state["response"] = "Some required details are missing. Please provide all required information before confirming the booking."
        if chat_history.get(session_id) and chat_history[session_id][-1]["sender"] == "bot":
            chat_history[session_id].pop()
        chat_history[session_id].append({"text": state["response"], "sender": "bot"})

    return state

def execute_actions(session_id: str, state: dict) -> dict:
    """
    Executes irreversible actions based on booking context and decision logic.
    """
    intent = state.get("last_intent")
    status = state.get("status")
    booking_number = state.get("booking_number")
    full_name = state.get("full_name")

    logging.info(f"[Session {session_id}] Action Dispatch — intent: {intent}, status: {status}, booking_number: {booking_number}, name: {full_name}")
    logging.info(f"[Session {session_id}] Booking context completeness check:")
    is_complete = is_booking_complete(state)

    # RESET
    if intent == "reset":
        booking_contexts[session_id] = {}
        chat_history[session_id] = []
        logging.info(f"[Session {session_id}] Reset executed.")
        return {
            "reply": INIT_PROMPT,
            "context": transform_context({}),
            "reset": True
        }

    # DB ENRICHMENT
    if booking_number and full_name and not is_complete:
        db_booking = get_booking_by_number_and_name(booking_number, full_name)
        if db_booking:
            logging.info(f"[Session {session_id}] Booking found in DB. Enriching state.")
            for key, value in db_booking.items():
                if not state.get(key):
                    state[key] = value

            # Re-check completeness and promote status if appropriate
            if is_booking_complete(state) and intent == "cancel":
                state["status"] = "confirmed"
                logging.info(f"[Session {session_id}] Booking context is now complete — promoting to 'confirmed' for cancellation.")

            # Fix misleading message from rectify_context
            if chat_history.get(session_id) and "Some required details are missing" in chat_history[session_id][-1]["text"]:
                chat_history[session_id].pop()

            # Respond after enrichment
            if intent == "smalltalk":
                state["response"] = "I’ve found your reservation. What would you like to do with your booking?"
            elif intent == "cancel":
                state["response"] = "Please confirm if you want to cancel this reservation."
            elif intent == "modify":
                state["response"] = "I've loaded your booking. What would you like to change?"
            else:
                state["response"] = "I’ve found your reservation and updated your booking details."
            chat_history[session_id].append({"text": state["response"], "sender": "bot"})

        else:
            logging.warning(f"[Session {session_id}] No booking found for name='{full_name}' and number='{booking_number}'")
            state["response"] = "Sorry, I couldn't find a booking with that name and number. Please double-check your details."
            state["booking_number"] = None
            chat_history[session_id].append({"text": state["response"], "sender": "bot"})

    # ❌ CANCEL: confirmed + intent cancel + booking_number
    if state.get("status") == "confirmed" and intent == "cancel" and booking_number:
        from database import remove_booking
        remove_booking(booking_number)
        logging.info(f"[Session {session_id}] Booking {booking_number} cancelled and removed from DB.")

        # Fully reset context and chat
        booking_contexts[session_id] = {}
        chat_history[session_id] = []

        response = "Your reservation has been cancelled as requested. If you'd like to make a new booking, just let me know!"
        chat_history[session_id].append({"text": response, "sender": "bot"})

        return {
            "reply": response,
            "context": transform_context({}),
            "reset": True
        }


    # ✅ CONFIRMATION: confirmed + complete + intent != cancel
    if state.get("status") == "confirmed" and is_booking_complete(state):
        if intent != "cancel":
            if not booking_number:
                state["booking_number"] = generate_booking_number()
            upsert_booking(state)
            logging.info(f"[Session {session_id}] Booking upserted into DB.")
            state["response"] = state.get("response", "Your booking is confirmed.")
            chat_history[session_id].append({"text": state["response"], "sender": "bot"})

    # 🧾 FALLBACK
    if not state.get("response"):
        state["response"] = "I'm here to help you with your booking."
        chat_history[session_id].append({"text": state["response"], "sender": "bot"})

    return {
        "reply": state["response"],
        "context": transform_context(state)
    }



# Initialize the database at startup
init_db()

@router.post("/")
def chat_endpoint(request: ChatRequest):
    session_id = request.sessionId
    user_message = request.message.strip()
    logging.info(f"[Session {session_id}] Received message: {user_message}")

    # Initialize session if needed
    if session_id not in booking_contexts:
        booking_contexts[session_id] = {}
        chat_history[session_id] = []
        chat_history[session_id].append({"text": INIT_PROMPT, "sender": "bot"})
        logging.info(f"[Session {session_id}] New session. Sending init message.")
        return {"reply": INIT_PROMPT, "context": transform_context({})}

    # Append user message
    chat_history[session_id].append({"text": user_message, "sender": "user"})

    # Compose full chat history
    conv_history = "\n".join(f"{msg['sender']}: {msg['text']}" for msg in chat_history[session_id])

    # Run LLM and update context
    updated_context = update_booking_context(conv_history, booking_contexts[session_id], user_message)

    # Rectify context if LLM logic was off
    updated_context = rectify_context(session_id, updated_context)

    # Save updated context in memory
    booking_contexts[session_id] = updated_context

    # Execute follow-up actions and return response
    return execute_actions(session_id, updated_context)

@router.get("/history")
def get_chat_history(sessionId: str = None):
    if sessionId and sessionId in chat_history:
        return {"history": chat_history[sessionId]}
    else:
        return {"history": []}
