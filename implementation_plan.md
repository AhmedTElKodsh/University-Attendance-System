# Implementation Plan

[Overview]
Develop the Mustian Face MVP, a web-based university attendance system using Face Recognition and Liveness Detection, with admin and doctor dashboards, student management, course/CRN/lecture management, and automated attendance recording via classroom device. The system will be built with Python FastAPI (backend), React (frontend), SQLite (database), and open-source AI libraries for face processing.

[Types]
Define data models for all system entities including User, Student, Doctor, Course, CRN, Lecture, AttendanceRecord, FaceProfile, and AttendanceEditLog. Each type includes fields, validation rules, and relationships as specified in the project documentation.

Detailed type definitions:
- User: id (int, PK), name (str), email (str, unique), password (str, hashed), role (enum: admin, doctor), status (enum: active, inactive), created_at (datetime), updated_at (datetime)
- Student: id (int, PK), student_id (str, unique), full_name (str), email (str, nullable), phone (str, nullable), faculty (str), department (str), academic_level (str), program (str), status (enum: active, inactive), created_at (datetime), updated_at (datetime)
- Doctor: id (int, PK), user_id (int, FK to User.id), staff_id (str, unique), full_name (str), email (str), phone (str, nullable), faculty (str), department (str), academic_title (str), status (enum: active, inactive), created_at (datetime), updated_at (datetime)
- Course: id (int, PK), course_name (str), course_code (str, unique), description (str, nullable), faculty (str), department (str), academic_year (str), semester (str), status (enum: active, inactive), created_at (datetime), updated_at (datetime)
- CRN: id (int, PK), crn (str, unique), course_id (int, FK to Course.id), doctor_id (int, FK to Doctor.id), day_of_week (enum: Sunday, Monday, etc.), start_time (time), end_time (time), location (str), room (str), status (enum: active, inactive), created_at (datetime), updated_at (datetime)
- Enrollment: id (int, PK), student_id (int, FK to Student.id), course_id (int, FK to Course.id), crn_id (int, FK to CRN.id), academic_year (str), semester (str), created_at (datetime), updated_at (datetime) (unique constraint: student_id + course_id)
- Lecture: id (int, PK), course_id (int, FK to Course.id), crn_id (int, FK to CRN.id), doctor_id (int, FK to Doctor.id), lecture_date (date), start_time (time), end_time (time), attendance_open_time (datetime), attendance_close_time (datetime), location (str), status (enum: scheduled, active, completed, cancelled), cancellation_reason (str, nullable), created_at (datetime), updated_at (datetime)
- AttendanceRecord: id (int, PK), lecture_id (int, FK to Lecture.id), student_id (int, FK to Student.id), course_id (int, FK to Course.id), crn_id (int, FK to CRN.id), status (enum: present, absent), attendance_time (datetime), recorded_by (int, FK to User.id, nullable), method (enum: face_recognition, manual), created_at (datetime), updated_at (datetime) (unique constraint: lecture_id + student_id)
- FaceProfile: id (int, PK), student_id (int, FK to Student.id, unique), face_embedding (blob), image_reference (str, nullable), confidence_threshold (float, default 0.6), created_at (datetime), updated_at (datetime)
- AttendanceEditLog: id (int, PK), attendance_record_id (int, FK to AttendanceRecord.id), lecture_id (int, FK to Lecture.id), student_id (int, FK to Student.id), doctor_id (int, FK to Doctor.id), old_status (enum: present, absent), new_status (enum: present, absent), reason (str), created_at (datetime)

[Files]
Create new files for backend, frontend, database, and configuration; no existing files to modify (empty project).

Detailed breakdown:
- New files to create:
  - Backend:
    - `backend/main.py` (FastAPI app entry point)
    - `backend/config.py` (configuration settings)
    - `backend/database.py` (SQLite database setup, SQLAlchemy models)
    - `backend/models.py` (Pydantic schemas for request/response)
    - `backend/routers/auth.py` (login endpoints)
    - `backend/routers/admin.py` (admin management endpoints)
    - `backend/routers/doctor.py` (doctor endpoints)
    - `backend/routers/student.py` (student management endpoints)
    - `backend/routers/course.py` (course/CRN/lecture endpoints)
    - `backend/routers/attendance.py` (attendance recording and management endpoints)
    - `backend/services/face_recognition.py` (face recognition logic)
    - `backend/services/liveness.py` (liveness detection logic)
    - `backend/services/attendance_service.py` (attendance business logic)
    - `backend/requirements.txt` (Python dependencies)
    - `backend/Dockerfile` (backend container config)
  - Frontend:
    - `frontend/src/App.jsx` (React app entry)
    - `frontend/src/pages/Login.jsx` (admin/doctor login)
    - `frontend/src/pages/admin/Dashboard.jsx` (admin dashboard)
    - `frontend/src/pages/admin/StudentManagement.jsx` (student management)
    - `frontend/src/pages/admin/DoctorManagement.jsx` (doctor management)
    - `frontend/src/pages/admin/CourseManagement.jsx` (course/CRN management)
    - `frontend/src/pages/admin/LectureManagement.jsx` (lecture management)
    - `frontend/src/pages/admin/Statistics.jsx` (system statistics)
    - `frontend/src/pages/doctor/Dashboard.jsx` (doctor dashboard)
    - `frontend/src/pages/doctor/CourseDetails.jsx` (course/lecture details)
    - `frontend/src/pages/doctor/AttendanceStatistics.jsx` (attendance stats)
    - `frontend/src/pages/attendance/AttendanceScreen.jsx` (classroom attendance screen)
    - `frontend/src/components/Navbar.jsx` (navigation bar)
    - `frontend/src/services/api.js` (API client)
    - `frontend/package.json` (frontend dependencies)
    - `frontend/Dockerfile` (frontend container config)
  - Root:
    - `docker-compose.yml` (multi-container setup)
    - `implementation_plan.md` (this document)
- Existing files to modify: None
- Files to delete/move: None

[Functions]
Implement new functions for API endpoints, business logic, and AI services.

Detailed breakdown:
- New functions:
  - `backend/main.py`: `create_app()` (initialize FastAPI app, include routers)
  - `backend/routers/auth.py`: `login()` (authenticate admin/doctor, return JWT)
  - `backend/routers/admin.py`: `create_student()`, `update_student()`, `delete_student()`, `assign_student_to_crn()`, `create_doctor()`, `update_doctor()`, `create_course()`, `create_crn()`, `schedule_lectures()`, `get_system_stats()`
  - `backend/routers/doctor.py`: `get_assigned_courses()`, `get_lecture_details()`, `add_attendance_manual()`, `remove_attendance_manual()`, `cancel_lecture()`, `get_attendance_stats()`
  - `backend/routers/attendance.py`: `start_attendance_session()`, `record_attendance()` (face recognition + liveness), `get_attendance_screen_data()`
  - `backend/services/face_recognition.py`: `register_face()` (store face embedding), `recognize_face()` (match captured face to embeddings)
  - `backend/services/liveness.py`: `check_liveness()` (verify real person)
  - `backend/services/attendance_service.py`: `validate_attendance()` (check course/CRN/enrollment), `record_attendance()` (save to DB)
  - Frontend: API call wrappers in `api.js`, React component handlers for form submissions, attendance screen camera logic.

[Classes]
Define new classes for database models (SQLAlchemy), Pydantic schemas, and service classes.

Detailed breakdown:
- New classes:
  - `backend/database.py`: `Base` (SQLAlchemy declarative base), `User`, `Student`, `Doctor`, `Course`, `CRN`, `Enrollment`, `Lecture`, `AttendanceRecord`, `FaceProfile`, `AttendanceEditLog` (all SQLAlchemy models with table definitions and relationships)
  - `backend/models.py`: Pydantic models for `UserCreate`, `UserLogin`, `StudentCreate`, `StudentUpdate`, `DoctorCreate`, `CourseCreate`, `CRNCreate`, `LectureCreate`, `AttendanceRecordCreate`, `AttendanceEditLogCreate`
  - `backend/services/face_recognition.py`: `FaceRecognitionService` (handle embedding generation and matching)
  - `backend/services/liveness.py`: `LivenessService` (handle liveness checks)
  - Frontend: React functional components (all pages and components listed in Files section)

[Dependencies]
Add new Python and Node.js dependencies for the MVP.

Details:
- Python (backend/requirements.txt): fastapi, uvicorn, sqlalchemy, pydantic, python-jose (JWT), passlib (password hashing), face-recognition, opencv-python, numpy, python-multipart (file uploads)
- Node.js (frontend/package.json): react, react-dom, react-router-dom, axios, jwt-decode, bootstrap (UI styling)

[Testing]
Implement unit and integration tests for critical functionality.

Test file requirements:
- Backend tests: `backend/tests/test_auth.py`, `backend/tests/test_attendance.py`, `backend/tests/test_admin.py` (test login, attendance recording, student management)
- Frontend tests: `frontend/src/__tests__/Login.test.js`, `frontend/src/__tests__/AttendanceScreen.test.js` (test login flow, attendance screen rendering)
- Validation strategies: Test face recognition accuracy, liveness detection, attendance business rules (duplicate records, CRN validation, time window)

[Implementation Order]
Execute changes in logical order to minimize conflicts.

Numbered steps:
1. Set up project directory structure (backend, frontend, root config files)
2. Configure backend: database models, SQLAlchemy setup, Pydantic schemas
3. Implement backend core services: face recognition, liveness detection, attendance business logic
4. Implement backend API routers: auth, admin, doctor, attendance
5. Set up frontend project with React, install dependencies, create base components
6. Implement frontend pages: login, admin dashboard, student/doctor/course management
7. Implement frontend attendance screen with camera integration
8. Implement doctor dashboard pages and attendance management
9. Add Docker configuration and docker-compose for containerization
10. Write and run tests for critical functionality
11. Verify end-to-end flow: admin creates data → doctor manages lectures → student records attendance via classroom screen.