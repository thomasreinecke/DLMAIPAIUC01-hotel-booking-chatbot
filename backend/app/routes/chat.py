from fastapi import APIRouter
from pydantic import BaseModel
import logging
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
router = APIRouter()
logging.basicConfig(level=logging.INFO)

# Get the absolute path to the system-prompts.json file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This points to /backend/app/routes/
PROMPTS_PATH = os.path.join(BASE_DIR, "../../system-prompts.json")  # Move up to /backend/

# ✅ Load System Prompts from JSON
with open(os.path.abspath(PROMPTS_PATH), "r") as f:
    PROMPTS = json.load(f)


# ✅ Environment variables
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://127.0.0.1:1234/v1")
MODEL = os.getenv("MODEL", "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF")

# Store user sessions & memory
user_sessions = {}
chat_history = []

# ✅ Request Model
class ChatRequest(BaseModel):
    message: str
    sessionId: str

# ✅ Intent Identification using LM Studio
def identify_intent(user_input):
    """ Uses LLM to determine the user's intent via LM Studio. """
    try:
        response = requests.post(
            f"{LMSTUDIO_URL}/chat/completions",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": PROMPTS["intent_identification"]},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.3,
            },
        )
        response.raise_for_status()
        intent = response.json()["choices"][0]["message"]["content"].strip().lower()
        return intent if intent in ["booking", "modify", "cancel", "confirm", "smalltalk"] else "smalltalk"

    except Exception as e:
        logging.error(f"Error in intent identification: {e}")
        return "smalltalk"

# ✅ General LLM Query Function
def query_llm(user_input, intent):
    """ Queries the local LM Studio instance for general responses based on intent. """
    try:
        response = requests.post(
            f"{LMSTUDIO_URL}/chat/completions",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": PROMPTS[intent]},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"Error in LLM response: {e}")
        return "I'm sorry, but I encountered an issue processing your request."

# ✅ Booking Conversation Flow
def handle_booking(user_id, user_input):
    """ Manages the booking conversation flow. """

    # Initialize user session if it doesn't exist
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "intent": "booking",
            "data": {},
            "history": []
        }

    session = user_sessions[user_id]
    session["history"].append({"role": "user", "content": user_input})

    # Required booking fields
    required_fields = ["guest name", "check-in date", "check-out date", "number of guests", "breakfast inclusion", "payment method"]
    
    # Determine missing fields
    missing_fields = [field for field in required_fields if field not in session["data"]]

    # If all fields are collected, confirm the booking
    if not missing_fields:
        return f"All details have been collected. Please confirm your booking: {session['data']}"

    # Ask the LLM what the next missing field is
    return query_llm(user_input, "booking")

# ✅ Chat API Endpoint
@router.post("/")
def chat(request: ChatRequest):
    """Handles user messages, identifies intent, and manages different chatbot tasks."""
    
    logging.info(f"Received message: {request.message} from session {request.sessionId}")

    # Initialize session if it doesn't exist
    if request.sessionId not in user_sessions:
        user_sessions[request.sessionId] = {"intent": None, "data": {}, "history": []}
        # Send initial greeting if session is new
        init_message = PROMPTS["init"]
        chat_history.append({"text": init_message, "sender": "bot"})
        return {"reply": init_message, "context": user_sessions[request.sessionId]}

    session = user_sessions[request.sessionId]

    # Identify user intent dynamically
    identified_intent = identify_intent(request.message)
    session["intent"] = identified_intent
    logging.info(f"Identified intent: {identified_intent}")

    # Handle different intents
    if identified_intent == "booking":
        bot_reply = handle_booking(request.sessionId, request.message)
    else:
        bot_reply = query_llm(request.message, identified_intent)  # Let LM Studio handle responses

    # Store response in history
    chat_history.append({"text": request.message, "sender": "user"})
    chat_history.append({"text": bot_reply, "sender": "bot"})

    return {"reply": bot_reply, "context": session}

# ✅ Chat History Endpoint
@router.get("/history")
def get_chat_history():
    """Fetch previous chat messages."""
    return {"history": chat_history}
