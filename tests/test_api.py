from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello, FastAPI!"

def test_create_student():
    # Use unique email to avoid duplicates
    unique_email = f"teststudent_{int(time.time() * 1000)}@example.com"
    resp = client.post("/students/", json={"name": "Test Student", "email": unique_email})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Test Student"
    assert data["email"] == unique_email

def test_create_and_fetch_faculty():
    # Use unique email to avoid duplicates
    unique_email = f"testfaculty_{int(time.time() * 1000)}@example.com"
    resp = client.post("/faculty/", json={"name": "Test Faculty", "email": unique_email})
    assert resp.status_code == 200
    faculty_id = resp.json()["id"]
    resp2 = client.get(f"/faculty/{faculty_id}")
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Test Faculty"

def test_create_course_and_enrollment():
    # Use unique emails to avoid duplicates
    student_email = f"enrollme_{int(time.time() * 1000)}@example.com"
    faculty_email = f"prof_{int(time.time() * 1000)}@example.com"
    student_resp = client.post("/students/", json={"name": "Enroll Me", "email": student_email})
    faculty_resp = client.post("/faculty/", json={"name": "Prof", "email": faculty_email})
    course_resp = client.post("/courses/", json={
        "name": "Science",
        "credits": 3,
        "faculty_id": faculty_resp.json()["id"]
    })
    enroll_resp = client.post("/enrollments/", json={
        "student_id": student_resp.json()["id"],
        "course_id": course_resp.json()["id"]
    })
    assert enroll_resp.status_code == 200
    data = enroll_resp.json()
    assert data["student_id"] == student_resp.json()["id"]
    assert data["course_id"] == course_resp.json()["id"]
