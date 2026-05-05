import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine
from models import UserCreate
from services import auth_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_admin_token():
    # Create admin user first
    from database import SessionLocal
    from models import User
    db = SessionLocal()
    admin = User(
        email="admin@test.com",
        name="Admin Test",
        role="admin",
        hashed_password=auth_service.get_password_hash("password123")
    )
    db.add(admin)
    db.commit()
    db.close()
    
    response = client.post("/auth/login", data={"username": "admin@test.com", "password": "password123"})
    return response.json()["access_token"]

def test_create_student():
    token = get_admin_token()
    response = client.post(
        "/students/",
        json={
            "student_id": "S12345",
            "full_name": "Test Student",
            "faculty": "Engineering",
            "department": "CS",
            "academic_level": "1",
            "program": "BSc"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["student_id"] == "S12345"

def test_get_students():
    token = get_admin_token()
    response = client.get("/students/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_course():
    token = get_admin_token()
    response = client.post(
        "/courses/",
        json={
            "course_name": "CS101",
            "course_code": "CS101",
            "faculty": "Engineering",
            "department": "CS"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["course_code"] == "CS101"