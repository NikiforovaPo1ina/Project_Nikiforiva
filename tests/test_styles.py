from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_styles():

    response = client.get("/styles")

    assert response.status_code == 200

    data = response.json()

    assert "styles" in data

    assert "anime" in data["styles"]