import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def test_create_course():
    faculty_resp = client.post(
        "/faculty/",
        json={"name": "Prof Course", "email": unique_email("coursefac")},
    )
    faculty_id = faculty_resp.json()["id"]
    course_resp = client.post(
        "/courses/",
        json={"name": "Science", "credits": 3, "faculty_id": faculty_id},
    )
    assert course_resp.status_code == 200
    data = course_resp.json()
    assert data["name"] == "Science"
    assert data["faculty_id"] == faculty_id

