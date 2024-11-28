from fastapi.testclient import TestClient
from app.main_old import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Talento SLATAM" in response.text