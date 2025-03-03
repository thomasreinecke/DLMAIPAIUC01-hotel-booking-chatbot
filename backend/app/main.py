from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, booking

app = FastAPI(title="Roomie Chatbot API")

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # Allow frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(booking.router, prefix="/booking", tags=["booking"])

@app.get("/")
def root():
    return {"message": "Roomie Chatbot API is running 🚀"}
