from fastapi import APIRouter
from pydantic import BaseModel
import logging
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()
logging.basicConfig(level=logging.INFO)

# Environment variables
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")  
API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio")  
MODEL = os.getenv("MODEL", "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF")  

# Initialize OpenAI client with LMStudio configuration
openai.api_base = LMSTUDIO_URL
openai.api_key = API_KEY

# User session context storage
user_sessions = {}

# Read system prompt from a dedicated file (system-prompt.txt)
def load_system_prompt():
    try:
        with open("system-prompt.txt", "r") as file:
            system_prompt = file.read().strip()
        return system_prompt
    except FileNotFoundError:
        logging.error("system-prompt.txt file not found. Using default prompt.")
        return "Always answer in rhymes."  # Default system message if file is not found

class ChatRequest(BaseModel):
    message: str
    sessionId: str  # Unique session ID from the frontend

def identify_intent(user_input):
    """ Uses the LLM to determine the user's intent. """
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Identify the user's intent as one of: booking, modify, cancel, confirm, smalltalk. Respond with only the intent word."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
        )

        intent = response.choices[0].message['content'].strip().lower()
        
        # Ensure valid intent
        if intent not in ["booking", "modify", "cancel", "confirm", "smalltalk"]:
            return "smalltalk"  # Default to smalltalk if intent is unclear
        
        return intent

    except Exception as e:
        logging.error(f"Error in intent identification: {e}")
        return "smalltalk"

@router.post("/")
def chat(request: ChatRequest):
    """Handles user messages, identifies intent, updates context, and returns chatbot response."""
    
    logging.info(f"Received message: {request.message} from session {request.sessionId}")

    # Initialize user session if it doesn't exist
    if request.sessionId not in user_sessions:
        user_sessions[request.sessionId] = {"intent": None, "data": {}}

    session = user_sessions[request.sessionId]

    # Identify user intent dynamically
    identified_intent = identify_intent(request.message)
    
    # Store or update intent
    session["intent"] = identified_intent
    logging.info(f"Identified intent: {identified_intent}")

    try:
        # Load system prompt
        system_prompt = load_system_prompt()

        # Generate chatbot response using the LLM
        completion = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
        )
        
        bot_reply = completion.choices[0].message['content']
        logging.info(f"Bot reply: {bot_reply}")

        # Store messages in chat history
        chat_history.append({"text": request.message, "sender": "user"})
        chat_history.append({"text": bot_reply, "sender": "bot"})

        # Return chatbot response & updated context
        return {"reply": bot_reply, "context": session}

    except Exception as e:
        logging.error(f"Error in generating response: {e}")
        return {"reply": "Sorry, there was an issue with processing your message.", "context": session}

# Store chat history in memory
chat_history = []

@router.get("/history")
def get_chat_history():
    """Fetch previous chat messages."""
    return {"history": chat_history}
