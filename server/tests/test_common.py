from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_404_returns_standard_error():
    resp = client.get("/api/v1/nonexistent-endpoint")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["code"] == "NOT_FOUND"


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
