import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db
from backend.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
def test_user(client):
    # Create a test user (admin)
    from backend.database import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("testpassword")
    
    db = TestingSessionLocal()
    user = User(
        name="Test Admin",
        email="admin@test.com",
        password=hashed_password,
        role="admin",
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    
    return {"email": "admin@test.com", "password": "testpassword"}

def test_login_success(client, test_user):
    response = client.post("/auth/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client, test_user):
    response = client.post("/auth/login", data={
        "username": test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "username": "nonexistent@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 401

def test_get_current_user(client, test_user):
    # Login first
    login_response = client.post("/auth/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]