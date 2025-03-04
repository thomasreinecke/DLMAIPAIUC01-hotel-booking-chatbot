from fastapi import APIRouter
from pydantic import BaseModel
import logging
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()
logging.basicConfig(level=logging.INFO)

# Environment variables
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")  # LMStudio local server URL
API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio")  # API key for LMStudio
MODEL = os.getenv("MODEL", "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF")  # API key for LMStudio


# Initialize OpenAI client with LMStudio configuration
openai.api_base = LMSTUDIO_URL
openai.api_key = API_KEY

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

@router.post("/")
def chat(request: ChatRequest):
    """Handles user messages and forwards them to LMStudio server."""
    
    logging.info(f"Received message: {request.message}")
    
    try:
        # Load the system prompt from the file
        system_prompt = load_system_prompt()

        # Call LMStudio API to get the response from Meta-Llama-3.1-8B-Instruct
        completion = openai.ChatCompletion.create(
            model=MODEL,  # selected Model
            messages=[
                {"role": "system", "content": system_prompt}, # System message loaded from file
                {"role": "user", "content": request.message}  # User's message
            ],
            temperature=0.7,
        )
        
        # Get the response and send it back
        bot_reply = completion.choices[0].message['content']
        logging.info(f"Bot reply: {bot_reply}")

        # Store messages in chat history
        chat_history.append({"text": request.message, "sender": "user"})
        chat_history.append({"text": bot_reply, "sender": "bot"})

        return {"reply": bot_reply}
    
    except Exception as e:
        logging.error(f"Error in generating response: {e}")
        return {"reply": "Sorry, there was an issue with processing your message."}

# Store chat history in memory
chat_history = []

@router.get("/history")
def get_chat_history():
    """Fetch previous chat messages."""
    return {"history": chat_history}
