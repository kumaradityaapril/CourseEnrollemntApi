import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_value(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello, FastAPI!"


def test_create_user_and_login():
    username = unique_value("user")
    email = f"{unique_value('user')}@example.com"
    payload = {
        "username": username,
        "email": email,
        "password": "secret123",
        "role": "student",
    }
    create_resp = client.post("/users/", json=payload)
    assert create_resp.status_code == 201
    token_resp = client.post(
        "/token",
        data={"username": username, "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    assert "access_token" in token_resp.json()

