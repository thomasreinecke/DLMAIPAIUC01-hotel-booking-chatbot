# DLMAIPAIUC01-hotel-booking-chatbot

make install      # Installs both frontend and backend dependencies
make run         # Runs frontend and backend together
make clean       # Cleans up virtual environment and node_modules
make test        # Runs backend tests


## run the backend

cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

