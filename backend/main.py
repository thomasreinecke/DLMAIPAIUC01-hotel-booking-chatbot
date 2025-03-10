import os
import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import your local modules directly
import chat
from llm import LMStudioLLM

load_dotenv()

app = FastAPI(title="Roomie Chatbot API")

# Environment variables
backend_hostname = os.getenv("BACKEND_HOSTNAME", "localhost")
backend_port = os.getenv("BACKEND_PORT", "8000")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(',')
model = os.getenv("MODEL", "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF")

logging.basicConfig(level=logging.INFO)

def check_llm_availability():
    """
    Ensures that the local LLM (LMStudio) is available before starting the API
    by making a simple test call to LMStudioLLM.
    """
    llm = LMStudioLLM()
    max_retries = 5
    retry_delay = 3  # seconds

    for attempt in range(max_retries):
        try:
            logging.info(f"🔄 Checking LLM availability... (Attempt {attempt + 1}/{max_retries})")
            response = llm.predict("Hello")  # simple test prompt
            if response:
                logging.info(f"✅ LLM '{model}' is available and ready to process requests.")
                return True
        except Exception as e:
            logging.error(f"❌ Error connecting to LLM: {e}")

        logging.info(f"Waiting {retry_delay} seconds before retrying...")
        asyncio.sleep(retry_delay)

    logging.error("❌ LLM is unavailable after multiple attempts. Exiting...")
    exit(1)

@app.on_event("startup")
async def startup_event():
    """Triggered on startup to ensure the local LLM is online."""
    logging.info("🚀 Roomie Chatbot API is starting up...")
    await asyncio.to_thread(check_llm_availability)
    logging.info(f"✅ API is now live at {backend_hostname}:{backend_port}")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("🛑 Roomie Chatbot API is shutting down...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your chat router from chat.py
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
def root():
    return {"message": "Roomie Chatbot API is running 🚀"}
