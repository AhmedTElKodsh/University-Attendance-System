from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./mustian_face.db"
    
    # JWT - REQUIRED in production
    SECRET_KEY: str = None  # Must be set via environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Face Recognition
    FACE_CONFIDENCE_THRESHOLD: float = 0.7  # Increased from 0.6 for better accuracy
    # COMMITTED: Simple face recognition (imagehash) - no dlib
    USE_SIMPLE_FACE_RECOGNITION: bool = True
    
    # Attendance Window (minutes)
    ATTENDANCE_WINDOW_MINUTES: int = 30
    
    # Upload directory for face images
    UPLOAD_DIR: str = "uploads/faces"

    # CORS - specify exact origins for production
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:80", "http://localhost"]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate SECRET_KEY in production
        if self.ENVIRONMENT == "production" and (not self.SECRET_KEY or self.SECRET_KEY == "mustian-face-secret-key-change-in-production"):
            raise ValueError(
                "SECRET_KEY must be set to a secure random value in production. "
                "Generate one with: openssl rand -hex 32"
            )


settings = Settings()