import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def test_create_and_fetch_faculty():
    resp = client.post(
        "/faculty/",
        json={"name": "Test Faculty", "email": unique_email("faculty")},
    )
    assert resp.status_code == 200
    faculty_id = resp.json()["id"]
    resp2 = client.get(f"/faculty/{faculty_id}")
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Test Faculty"

