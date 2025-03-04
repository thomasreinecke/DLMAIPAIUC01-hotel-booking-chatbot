from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routes import chat, booking
import logging

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Roomie Chatbot API")

# Access environment variables
backend_hostname = os.getenv("BACKEND_HOSTNAME", "localhost")
backend_port = os.getenv("BACKEND_PORT", "8000")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(',')

# Log server startup information
logging.basicConfig(level=logging.INFO)
logging.info(f"Server starting up on {backend_hostname}:{backend_port} with CORS allowed from: {cors_origins}")

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Read from .env
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(booking.router, prefix="/booking", tags=["booking"])

@app.on_event("startup")
async def startup_event():
    """Event triggered when the app starts up."""
    logging.info(f"Roomie Chatbot API is starting up at {backend_hostname}:{backend_port}...")

@app.on_event("shutdown")
async def shutdown_event():
    """Event triggered when the app shuts down."""
    logging.info("Roomie Chatbot API is shutting down...")

@app.get("/")
def root():
    return {"message": "Roomie Chatbot API is running 🚀"}
