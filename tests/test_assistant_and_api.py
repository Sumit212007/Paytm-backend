from fastapi.testclient import TestClient
from app.main import app
from app.database.models import Merchant

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_dashboard_endpoint(db):
    # Test seeded merchant dashboard
    res = client.get("/api/v1/dashboard/mer_sharma_001")
    assert res.status_code == 200
    data = res.json()
    assert "merchant" in data
    assert "today" in data
    assert data["merchant"]["name"] == "Ramesh Sharma"


def test_assistant_chat_endpoint(db):
    payload = {
        "merchant_id": "mer_sharma_001",
        "message": "Aaj sales kam kyu hui?",
        "language": "hinglish"
    }
    res = client.post("/api/v1/assistant/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "message" in data
    assert data["audio_ready"] is True
    assert data["language"] == "hinglish"
