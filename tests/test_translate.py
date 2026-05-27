from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_translate():

    payload = {
        "text": "кот"
    }

    response = client.post(
        "/translate",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "translated" in data