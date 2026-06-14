import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.alert_store import reset as reset_store


@pytest.fixture(autouse=True)
def clear_alerts():
    reset_store()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "behavioral-anomaly-fastapi"


def test_alerts_returns_list(client):
    response = client.get("/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ingest_valid_events(client):
    events = [
        {
            "student_id": "S001",
            "timestamp": "2026-06-13T10:00:00",
            "activity_type": "login",
            "duration_minutes": 5,
            "sentiment_score": -0.7,
            "missed_classes": 3,
            "assignment_delay_days": 5,
            "social_interaction_score": 0.2,
        }
    ]
    response = client.post("/ingest", json=events)
    assert response.status_code == 200
    data = response.json()
    assert data["processed_events"] == 1
    assert data["alerts_generated"] >= 1
    assert "LOW" in data["risk_summary"]
    assert "MEDIUM" in data["risk_summary"]
    assert "HIGH" in data["risk_summary"]


def test_ingest_rejects_invalid_json(client):
    response = client.post("/ingest", json={"not": "an array"})
    assert response.status_code == 422


def test_ingest_rejects_missing_fields(client):
    response = client.post("/ingest", json=[{"student_id": "S001"}])
    assert response.status_code == 422


def test_reset_clears_alerts(client):
    events = [
        {
            "student_id": "S001",
            "timestamp": "2026-06-13T10:00:00",
            "activity_type": "login",
            "duration_minutes": 5,
            "sentiment_score": -0.7,
            "missed_classes": 3,
            "assignment_delay_days": 5,
            "social_interaction_score": 0.2,
        }
    ]
    client.post("/ingest", json=events)
    alerts = client.get("/alerts").json()
    assert len(alerts) > 0

    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    alerts_after = client.get("/alerts").json()
    assert len(alerts_after) == 0


def test_student_alerts_filtering(client):
    events = [
        {
            "student_id": "S001",
            "timestamp": "2026-06-13T10:00:00",
            "activity_type": "login",
            "duration_minutes": 5,
            "sentiment_score": -0.7,
            "missed_classes": 3,
            "assignment_delay_days": 5,
            "social_interaction_score": 0.2,
        },
        {
            "student_id": "S002",
            "timestamp": "2026-06-13T10:00:00",
            "activity_type": "login",
            "duration_minutes": 45,
            "sentiment_score": 0.6,
            "missed_classes": 0,
            "assignment_delay_days": 0,
            "social_interaction_score": 0.85,
        },
    ]
    client.post("/ingest", json=events)

    s001_alerts = client.get("/alerts/S001").json()
    assert all(a["student_id"] == "S001" for a in s001_alerts)

    s002_alerts = client.get("/alerts/S002").json()
    assert all(a["student_id"] == "S002" for a in s002_alerts)


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "total_events_processed" in response.text
