from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_stats():

    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert "total_generations" in data