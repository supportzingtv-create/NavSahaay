import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"
from app import create_app, db

def test_home():
    app=create_app()
    client=app.test_client()
    response=client.get("/")
    assert response.status_code==200
    assert b"Shivoham Foundation" in response.data

def test_api_stats():
    app=create_app()
    client=app.test_client()
    response=client.get("/api/stats")
    assert response.status_code==200
    assert b"donations" in response.data
