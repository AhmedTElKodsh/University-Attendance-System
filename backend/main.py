from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.database import create_tables
from backend.routers import auth, admin, doctor, attendance, student, course
from backend.config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Mustian Face MVP API",
    description="Web-based university attendance system using Face Recognition and Liveness Detection",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(doctor.router)
app.include_router(attendance.router)
app.include_router(student.router)
app.include_router(course.router)

@app.on_event("startup")
async def startup_event():
    create_tables()
    # Seed initial admin user
    try:
        from backend.seed import seed_admin
        seed_admin()
    except Exception as e:
        print(f"Warning: Could not seed admin user: {e}")

@app.get("/")
async def root():
    return {
        "message": "Mustian Face MVP API is running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth/login",
            "admin": "/admin/...",
            "doctor": "/doctor/...",
            "attendance": "/attendance/..."
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
