import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def test_create_course_and_enrollment():
    student_resp = client.post(
        "/students/",
        json={"name": "Enroll Me", "email": unique_email("enroll")},
    )
    faculty_resp = client.post(
        "/faculty/",
        json={"name": "Prof", "email": unique_email("prof")},
    )
    course_resp = client.post(
        "/courses/",
        json={
            "name": "Science",
            "credits": 3,
            "faculty_id": faculty_resp.json()["id"],
        },
    )
    enroll_resp = client.post(
        "/enrollments/",
        json={
            "student_id": student_resp.json()["id"],
            "course_id": course_resp.json()["id"],
        },
    )
    assert enroll_resp.status_code == 200
    data = enroll_resp.json()
    assert data["student_id"] == student_resp.json()["id"]
    assert data["course_id"] == course_resp.json()["id"]

