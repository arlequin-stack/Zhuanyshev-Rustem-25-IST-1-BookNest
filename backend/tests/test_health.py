from fastapi.testclient import TestClient
from app.main import app

def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_openapi_contains_core_routes():
    schema = TestClient(app).get("/api/openapi.json").json()
    for path in ("/api/v1/books", "/api/v1/auth/register", "/api/v1/loans"):
        assert path in schema["paths"]

