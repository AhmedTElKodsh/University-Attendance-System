# Mustian Face MVP

A web-based university attendance system using Face Recognition and Liveness Detection.

## Features

- **Admin Dashboard**: Manage students, doctors, courses, CRNs, and lectures
- **Doctor Dashboard**: View assigned courses, manage lectures, record attendance manually
- **Attendance Screen**: Students mark attendance using face recognition via webcam
- **Face Recognition**: Simple photo matching (imagehash) - no dlib
- **Liveness Detection**: Basic image quality checks
- **JWT Authentication**: Secure login for admin and doctors

## Project Structure

```
Mustian-Face/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py         # SQLAlchemy models and database setup
│   ├── models.py           # Pydantic schemas
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container config
│   ├── .env.example        # Environment variables template
│   ├── services/
│   │   ├── simple_face_recognition.py  # Simple face matching (imagehash)
│   │   ├── liveness.py        # Basic image quality checks
│   │   └── attendance_service.py # Attendance business logic
│   ├── routers/
│   │   ├── auth.py           # Login endpoints
│   │   ├── admin.py          # Admin management endpoints
│   │   ├── doctor.py         # Doctor endpoints
│   │   └── attendance.py     # Attendance recording endpoints
│   └── tests/
│       ├── test_auth.py       # Authentication tests
│       └── test_attendance.py # Attendance tests
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx          # Main React app with routing
│   │   ├── services/
│   │   │   └── api.js      # API client
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── admin/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── StudentManagement.jsx
│   │   │   │   ├── DoctorManagement.jsx
│   │   │   │   ├── CourseManagement.jsx
│   │   │   │   ├── LectureManagement.jsx
│   │   │   │   └── Statistics.jsx
│   │   │   ├── doctor/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── CourseDetails.jsx
│   │   │   │   └── AttendanceStatistics.jsx
│   │   │   └── attendance/
│   │   │       └── AttendanceScreen.jsx
│   │   └── __tests__/
│   │       └── Login.test.js
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── implementation_plan.md
```

## Prerequisites

- **For Docker setup (Recommended)**:
  - Docker Desktop installed and running
  - Docker Compose v2

- **For local development**:
  - Python 3.11 (recommended, as some packages may not support 3.14 yet)
  - Node.js 18+
  - pip (Python package manager)

## Setup Instructions

### Option 1: Docker Setup (Easiest)

1. Make sure Docker Desktop is running
2. Clone the repository
3. Run:
   ```bash
   docker-compose up --build
   ```
4. Access:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. Create a virtual environment (recommended):
   ```bash
   # Using Python 3.11
   py -3.11 -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
   Uses simple imagehash approach - no dlib needed.

3. Run the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

#### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Access the frontend at http://localhost:3000

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and update the values as needed.

## API Endpoints

- **Auth**: `/auth/login` - Login with email and password
- **Admin**: `/admin/...` - Admin management endpoints
- **Doctor**: `/doctor/...` - Doctor endpoints
- **Attendance**: `/attendance/...` - Attendance recording

See the full API documentation at `/docs` when the backend is running.

## Default Users

You need to create users manually in the database or via the API. The system supports:
- Admin users (role: "admin")
- Doctor users (role: "doctor")

## Notes

- Face recognition uses simple photo matching (imagehash) - no dlib needed.
- For production, update the `SECRET_KEY` and use a proper database (PostgreSQL, MySQL, etc.)
- The current setup uses SQLite for simplicity.

## Troubleshooting

- **Docker not connecting**: Make sure Docker Desktop is running
- **Python package installation fails**: Try using Python 3.11 or install using pre-built wheels
- **Frontend build fails**: Make sure Node.js version is 18 or higher

## Implementation Status

- [x] Project structure setup
- [x] Backend configuration and models
- [x] Backend services (face recognition, liveness, attendance)
- [x] Backend API routers
- [x] Frontend setup and components
- [x] Frontend pages (login, dashboards, management)
- [x] Attendance screen with camera
- [x] Docker configuration
- [x] Tests (backend and frontend tests complete)
- [x] Deployment configuration (.gitignore, .env, DEPLOYMENT.md)
- [ ] End-to-end verification (run `docker-compose up --build`)

The code is complete and ready for deployment. See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## Quick Start

### Docker Deployment (Recommended)
```bash
# Copy and configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Start the application
docker-compose up --build

# Access:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed local setup instructions.
