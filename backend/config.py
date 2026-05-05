from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./mustian_face.db"
    
    # JWT
    SECRET_KEY: str = "mustian-face-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Face Recognition
    FACE_CONFIDENCE_THRESHOLD: float = 0.6
    # COMMITTED: Simple face recognition (imagehash) - no dlib
    USE_SIMPLE_FACE_RECOGNITION: bool = True
    
    # Attendance Window (minutes)
    ATTENDANCE_WINDOW_MINUTES: int = 30
    
    # Upload directory for face images
    UPLOAD_DIR: str = "uploads/faces"

    # CORS - specify exact origins for production
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:80", "http://localhost"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()