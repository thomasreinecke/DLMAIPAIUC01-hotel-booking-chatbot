# DLMAIPAIUC01-hotel-booking-chatbot

Hotel Booking chatbot implementation for IU course DLMAIPAIUC01: AI Project use Case

![Image](https://github.com/user-attachments/assets/24775eac-c9bb-4522-96a7-50902aeefc59)

**Roomie**, the hotel room booking chatbot of the fictional **Quantum Suites Hotel** supports the following use cases:

- **Booking** – Users can book their hotel stays. The chatbot collects the Guest name, Check-in date, Check-out date, Number of guests, Breakfast inclusion, and the Payment method. Bookings result in the issuance of a confirmation number, which is required for future modifications or cancellations.
- **Modification** – Users can modify an existing booking by providing their confirmation number and specifying the details to be updated. The system retrieves the reservation, applies the changes, and returns an updated confirmation.
- **Cancellation** – Users can cancel their reservation by providing their confirmation number. The chatbot confirms the action and removes the booking from the system.
- **Confirmation** – Users can request details of their booking using their confirmation number.
- **Small Talk** – Users may engage in casual conversations, such as greetings or farewells.

## System Architecture

<img width="1611" alt="Image" src="https://github.com/user-attachments/assets/1fbe061b-6875-4a59-97c4-68c184f27307" />

## List of dependencies

tbd

## setup LMStudio

instructions to be added

## install dependencies

## run the chatbot

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

