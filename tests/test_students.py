import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def test_create_student():
    resp = client.post(
        "/students/",
        json={"name": "Test Student", "email": unique_email("student")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Test Student"


def unique_value(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_students_pagination_and_total():
    created_ids = []
    for _ in range(5):
        resp = client.post(
            "/students/",
            json={
                "name": unique_value("Student"),
                "email": f"{unique_value('student')}@example.com",
            },
        )
        assert resp.status_code == 201
        created_ids.append(resp.json()["id"])

    list_resp = client.get("/students/?skip=0&limit=2")
    assert list_resp.status_code == 200
    data = list_resp.json()

    assert "total" in data
    assert "items" in data
    assert data["total"] >= 5
    assert len(data["items"]) == 2


def test_students_filter_by_name():
    name = "FilterTestStudent"
    email = f"{unique_value('filter')}@example.com"
    resp = client.post("/students/", json={"name": name, "email": email})
    assert resp.status_code == 201

    list_resp = client.get("/students/?name=FilterTest")
    assert list_resp.status_code == 200
    data = list_resp.json()

    assert data["total"] >= 1
    names = [item["name"] for item in data["items"]]
    assert any(entry == "FilterTestStudent" for entry in names)

