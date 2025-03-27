import pytest
from fastapi.testclient import TestClient
from chat import chat_endpoint, rectify_context, execute_actions, transform_context
from database import init_db, upsert_booking, get_booking_by_number_and_name, remove_booking
from main import app

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    yield

def test_initial_session_creation():
    session_id = "test_session_1"
    response = client.post("/chat", json={"sessionId": session_id, "message": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "context" in data
    assert data["context"]["status"] == "draft"

def test_booking_upsert_and_retrieval():
    context = {
        "booking_number": "ABC123",
        "full_name": "Jane Doe",
        "check_in_date": "2025-04-01",
        "check_out_date": "2025-04-04",
        "num_guests": 2,
        "payment_method": "Credit Card",
        "breakfast_included": "Yes",
        "status": "confirmed",
        "language": "English"
    }
    upsert_booking(context)
    booking = get_booking_by_number_and_name("ABC123", "Jane Doe")
    assert booking is not None
    assert booking["full_name"] == "Jane Doe"
    assert booking["status"] == "confirmed"

def test_remove_booking():
    remove_booking("ABC123")
    booking = get_booking_by_number_and_name("ABC123", "Jane Doe")
    assert booking is None

def test_transform_context_fields():
    context = {
        "last_intent": "book",
        "status": "confirmed",
        "full_name": "John Doe",
        "check_in_date": "2025-04-10",
        "check_out_date": "2025-04-15",
        "num_guests": 1,
        "breakfast_included": True,
        "payment_method": "PayPal",
        "booking_number": "XYZ789",
        "language": "English"
    }
    transformed = transform_context(context)
    assert transformed["intent"] == "book"
    assert transformed["status"] == "confirmed"
    assert transformed["data"]["guest name"] == "John Doe"

def test_rectify_context_invalid_status():
    session_id = "test_session_2"
    state = {"status": "done", "last_intent": "book"}
    updated = rectify_context(session_id, state)
    assert updated["status"] == "draft"

def test_rectify_context_missing_identity():
    session_id = "test_session_3"
    state = {"status": "confirmed", "last_intent": "cancel"}

    # Ensure chat history dict is initialized
    from chat import chat_history
    chat_history[session_id] = []  # 👈 fix here

    updated = rectify_context(session_id, state)
    assert "provide your full name" in updated["response"]
    assert chat_history[session_id][-1]["text"] == updated["response"]


def test_execute_action_reset():
    session_id = "test_session_4"
    state = {"last_intent": "reset"}
    result = execute_actions(session_id, state)
    assert result["reset"] is True
    assert result["context"]["status"] == "draft"

def test_api_get_history():
    session_id = "test_session_5"
    client.post("/chat", json={"sessionId": session_id, "message": "Hello again"})
    response = client.get(f"/chat/history?sessionId={session_id}")
    assert response.status_code == 200
    history = response.json()["history"]
    assert len(history) > 0
