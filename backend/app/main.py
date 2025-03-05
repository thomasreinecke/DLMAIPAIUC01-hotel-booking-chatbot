from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import asyncio
import requests
from dotenv import load_dotenv
from app.routes import chat, booking

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Roomie Chatbot API")

# Access environment variables
backend_hostname = os.getenv("BACKEND_HOSTNAME", "localhost")
backend_port = os.getenv("BACKEND_PORT", "8000")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(',')

# Log server startup information
logging.basicConfig(level=logging.INFO)

# ✅ Check if LLM is available at startup
def check_llm_availability():
    """Ensures that the LLM service is available before starting the API."""
    lmstudio_url = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")
    api_key = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
    model = os.getenv("MODEL", "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF")

    max_retries = 5
    retry_delay = 3  # seconds

    for attempt in range(max_retries):
        try:
            logging.info(f"🔄 Checking LLM availability... (Attempt {attempt + 1}/{max_retries})")
            response = requests.post(
                f"{lmstudio_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model, "messages": [{"role": "user", "content": "Hello"}]}
            )
            
            if response.status_code == 200:
                logging.info("✅ LLM is available and ready to process requests.")
                return True
            else:
                logging.warning(f"⚠️ LLM response status: {response.status_code}. Retrying...")
        except Exception as e:
            logging.error(f"❌ Error connecting to LLM: {e}")

        logging.info(f"Waiting {retry_delay} seconds before retrying...")
        asyncio.sleep(retry_delay)  # Ensure this runs synchronously

    logging.error("❌ LLM is unavailable after multiple attempts. Exiting...")
    exit(1)  # Hard exit to prevent FastAPI from running

# ✅ Ensure LLM is checked before FastAPI starts
@app.on_event("startup")
async def startup_event():
    """Event triggered when the app starts up."""
    logging.info("🚀 Roomie Chatbot API is starting up...")
    await asyncio.to_thread(check_llm_availability)  # Ensure this blocks startup
    logging.info(f"✅ API is now live at {backend_hostname}:{backend_port}")

@app.on_event("shutdown")
async def shutdown_event():
    """Event triggered when the app shuts down."""
    logging.info("🛑 Roomie Chatbot API is shutting down...")

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(booking.router, prefix="/booking", tags=["booking"])

@app.get("/")
def root():
    return {"message": "Roomie Chatbot API is running 🚀"}
