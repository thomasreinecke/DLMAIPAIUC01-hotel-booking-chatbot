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

<img width="1619" alt="Image" src="https://github.com/user-attachments/assets/edf9f105-287a-4ad1-80e5-0c2e169a3613" />

## List of dependencies

### Frontend dependencies

- [Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference), used as programming language to create dynamic web applications on the browser
- [NodeJS](https://nodejs.org/) as Javascript/Typescript runtime to provide the frontend application to the browser
- [Svelte](https://svelte.dev/) as Frontend Javascript framework, that compiles web components into highly optimized vanilla javascript
- [SvelteKit](https://svelte.dev/docs/kit/introduction) as Full-Stack development framework, providing Server-Side rendering (SSR), static site generation (SSG) and API routing using Svelte
- [Skeleton.dev](https://www.skeleton.dev/) as UI component library for Svelte and Sveltekit using Tailwind CSS, providing pre-defined, accessible and customizable web components for rapid web development   
- [TailwindCSS](https://tailwindcss.com/) as utility-first CSS framework that provides low-level utility classes to build custom designs quickly without writing custom CSS

### Backend dependencies

- [Python](https://www.python.org/), used as backend programming language to enable API development, database management and business logic handling 
- [Uvicorn](https://www.uvicorn.org/) as Asynchronous Server Gateway Interface (ASGI) to efficiently run asynchronous API services
- [FastAPI](https://fastapi.tiangolo.com/) as high performance Python web framework for building APIs
- [LangChain](https://www.langchain.com/), used as AI application development framework, specifically used for prompt embedding
- [LMStudio](https://lmstudio.ai/), used as local LLM server to run AI models efficiently on local hardware
- [SQLite](https://www.sqlite.org/), used as a lightweight, file-based database, ideal for local applications and embedded systems with simple data storage needs
- [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3), as open-source LLMs, providing NLP, intent identification, user input extraction and casual conversation capabilities

## setup LMStudio

LMStudio is an application to discover, download and run LLMs locally. In this project, LMStudio was used to evaluate various LLMs and their fit for purpose including `llama-3.2-1b-instruct`, `llama-3.2-3b-instruct`, `granite-3.2-8b-instruct`, `deepseek-r1-distill-llama-8b`. Best results were achieved using `mistral-7b-instruct-v0.3`.

To run LLMs locally, appropriate hardware (including GPUs) is highly recommended. This project was developed on an Apple Mac M1 Max. To setup LMStudio and run LLMs locally, following these steps:

- download LMStudio from https://lmstudio.ai/
- in LMStudio > Discover > search for the name of the LLM -> `mistral-7b-instruct-v0.3` or use this link ([Mistral-7B-Instruct-v0.3-GGUF Download](https://model.lmstudio.ai/download/lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF)
)
- switch LMStudio into the Developer mode (a button group at the bottom of the app)
- select the Developer view > select the model at the top > enable LMStudio Server, which would expose the model via a REST interface at http://127.0.0.1:1234
- with this the model is ready to be used as a REST service by the Chatbot

## clone project and install dependencies

```
git clone https://github.com/thomasreinecke/DLMAIPAIUC01-hotel-booking-chatbot.git
cd DLMAIPAIUC01-hotel-booking-chatbot
make
```

This will install both, the frontend and backend dependencies.

## run the chatbot

### start the backend
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

### start the frontend
```
cd frontend
./run.sh
```
or 
```
cd frontend
npm run dev
```

The frontend will usually start at http://localhost:5173 (port could vary)

## Chatbot status flow

* draft - if any of the required fields `full_name, check_in_date, check_out_date, num_guests, breakfast_included, payment_method` was not provided
* pending - if all of the required fields are populated, indicates ready for confirmation
* confirmed - if the user has confirmed the booking

## Supported user intends

* "book" - create a new booking. user is asked to fill all the fields necessary and confirm to save the booking
* "modify" - based on full name and the booking number a previously created booking is retrieved and can be modified
* "cancel" - based on full name and the booking number a previously created booking is retrieved and can be cancelled (and deleted)
* "reset" - a user can indicate to start the session over 
* "smalltalk" - engage with the chatbot in casual communication, the chatbot will try to lead back to the booking

## Unit testing

run the backend unit tests:

```
cd backend
pytest unit_tests.py
```
