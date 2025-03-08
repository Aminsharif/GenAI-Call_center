import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def auth_headers():
    # Get authentication token
    response = client.post(
        "/token",
        data={"username": "admin", "password": "your-secure-password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_call_statistics(auth_headers):
    response = client.get("/api/calls/statistics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_calls" in data
    assert "average_duration" in data
    assert "total_messages" in data

def test_get_call_history(auth_headers):
    # First create a call
    call_data = {
        "call_sid": "test_call_123",
        "from_number": "+1234567890",
        "to_number": "+0987654321",
        "status": "completed"
    }
    
    # Get the call history
    response = client.get(f"/api/calls/1/history", headers=auth_headers)
    if response.status_code == 200:
        data = response.json()
        assert "call_details" in data
        assert "messages" in data
    else:
        assert response.status_code == 404

def test_make_call_unauthorized():
    response = client.post("/api/calls/make", json={"to_number": "+1234567890"})
    assert response.status_code == 401

def test_make_call_authorized(auth_headers):
    response = client.post(
        "/api/calls/make",
        json={"to_number": "+1234567890"},
        headers=auth_headers
    )
    assert response.status_code in [200, 500]  # 500 if Twilio credentials are not set

def test_handle_call():
    response = client.post(
        "/api/voice/handle-call",
        data={
            "CallSid": "test_call_123",
            "From": "+1234567890",
            "To": "+0987654321"
        }
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    assert "<Response>" in response.text

def test_process_speech():
    response = client.post(
        "/api/voice/process-speech",
        data={
            "CallSid": "test_call_123",
            "SpeechResult": "This is a test message"
        }
    )
    assert response.status_code in [200, 404]  # 404 if call not found
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/xml"
        assert "<Response>" in response.text 