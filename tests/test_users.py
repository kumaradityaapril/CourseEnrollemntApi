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


def test_update_user_profile():
    """Test that a user can update their own profile."""
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
    user_id = create_resp.json()["id"]

    # Login to get token
    token_resp = client.post(
        "/token",
        data={"username": username, "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]

    # Update profile
    new_username = unique_value("updated")
    new_email = f"{unique_value('updated')}@example.com"
    update_payload = {"username": new_username, "email": new_email}
    update_resp = client.patch(
        f"/users/{user_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_resp.status_code == 200
    updated_user = update_resp.json()
    assert updated_user["username"] == new_username
    assert updated_user["email"] == new_email
    assert updated_user["id"] == user_id


def test_update_user_profile_unauthorized():
    """Test that a user cannot update another user's profile."""
    # Create first user
    username1 = unique_value("user1")
    email1 = f"{unique_value('user1')}@example.com"
    payload1 = {
        "username": username1,
        "email": email1,
        "password": "secret123",
        "role": "student",
    }
    create_resp1 = client.post("/users/", json=payload1)
    assert create_resp1.status_code == 201
    user_id1 = create_resp1.json()["id"]

    # Create second user
    username2 = unique_value("user2")
    email2 = f"{unique_value('user2')}@example.com"
    payload2 = {
        "username": username2,
        "email": email2,
        "password": "secret123",
        "role": "student",
    }
    create_resp2 = client.post("/users/", json=payload2)
    assert create_resp2.status_code == 201

    # Login as second user
    token_resp = client.post(
        "/token",
        data={"username": username2, "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]

    # Try to update first user's profile (should fail)
    update_payload = {"username": "hacked"}
    update_resp = client.patch(
        f"/users/{user_id1}",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_resp.status_code == 403
    assert "Not allowed to update profile" in update_resp.json()["detail"]

