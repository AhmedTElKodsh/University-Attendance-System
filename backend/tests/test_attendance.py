import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db, User, Student, Course, CRN, Lecture, Enrollment
from backend.config import settings
from passlib.context import CryptContext

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_attendance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def setup_test_data(client):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("testpassword")
    
    db = TestingSessionLocal()
    
    # Create admin user
    admin = User(name="Admin", email="admin@test.com", password=hashed_password, role="admin", status="active")
    db.add(admin)
    
    # Create doctor user
    doctor_user = User(name="Doctor", email="doctor@test.com", password=hashed_password, role="doctor", status="active")
    db.add(doctor_user)
    db.commit()
    
    # Create student
    student = Student(student_id="S001", full_name="Test Student", faculty="CS", department="IT", academic_level="1", program="CS")
    db.add(student)
    
    # Create doctor
    doctor = Doctor(user_id=doctor_user.id, staff_id="D001", full_name="Test Doctor", email="doctor@test.com", faculty="CS", department="IT", academic_title="Professor")
    db.add(doctor)
    
    # Create course
    course = Course(course_name="Test Course", course_code="TC101", faculty="CS", department="IT", academic_year="2024", semester="Fall")
    db.add(course)
    db.commit()
    
    # Create CRN
    crn = CRN(crn="12345", course_id=course.id, doctor_id=doctor.id, day_of_week="Monday", start_time="09:00", end_time="10:00", location="Building A", room="101", status="active")
    db.add(crn)
    db.commit()
    
    # Create lecture
    from datetime import datetime, time
    lecture = Lecture(
        course_id=course.id,
        crn_id=crn.id,
        doctor_id=doctor.id,
        lecture_date=datetime.now().date(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        attendance_open_time=datetime.now(),
        attendance_close_time=datetime.now(),
        location="Building A",
        status="scheduled"
    )
    db.add(lecture)
    
    # Create enrollment
    enrollment = Enrollment(student_id=student.id, course_id=course.id, crn_id=crn.id, academic_year="2024", semester="Fall")
    db.add(enrollment)
    
    db.commit()
    db.close()
    
    return {
        "student_id": student.id,
        "lecture_id": lecture.id,
        "course_id": course.id,
        "crn_id": crn.id
    }

def test_start_attendance_session(client, setup_test_data):
    # Login as admin
    login_response = client.post("/auth/login", data={"username": "admin@test.com", "password": "testpassword"})
    token = login_response.json()["access_token"]
    
    # Start attendance session
    response = client.put(f"/attendance/session/{setup_test_data['lecture_id']}/start", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()

def test_get_attendance_screen(client, setup_test_data):
    response = client.get(f"/attendance/screen/{setup_test_data['crn_id']}")
    assert response.status_code == 200
    assert "lecture_id" in response.json()