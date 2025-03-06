# DLMAIPAIUC01-hotel-booking-chatbot

```
make install     # Installs both frontend and backend dependencies
make run         # Runs frontend and backend together
make clean       # Cleans up virtual environment and node_modules
make test        # Runs backend tests
```

<img width="1097" alt="Image" src="https://github.com/user-attachments/assets/e0354848-8e37-4560-ac27-a9763b0817a2" />

## setup LMStudio

instructions to be added

## run the backend

```
cd backend
./run.sh
```

or

```
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```


# die intent identification ist unsinn. wir sollten den chat IMMER an das LLM direkt geben um entweder eine Buchung aufzunehmen
# oder eine bestehende aufzusuchen und weiter zu prozessieren. Das LLM sollte dabei die commands an das state management geben
# (z.b. retrieve by booking number or cancel or confirm)
# ich denke auch wir sollten kein auto-confirm machen, sondern den user sobald alles komplett ist explizit fragen ob er confirmen
# möchte. ich würde dennoch den letzten intend extrahieren lassen und auch auf smalltalk eingehen, ABER das LLM immer wieder zum
# eigentlichen ziel der reservierung zurück kehren lassen

