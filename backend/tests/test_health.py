from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_success_envelope() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Success"
    assert body["data"]["status"] == "ok"
