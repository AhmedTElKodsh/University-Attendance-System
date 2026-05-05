from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Time, Date, Enum, 
    ForeignKey, UniqueConstraint, LargeBinary, Float, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, create_engine
from datetime import datetime, timezone
import enum
import os

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"

class Status(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class DayOfWeek(str, enum.Enum):
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"

class LectureStatus(str, enum.Enum):
    scheduled = "scheduled"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"

class RecordMethod(str,enum.Enum):
    face_recognition = "face_recognition"
    manual = "manual"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(Status), default=Status.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    doctor = relationship("Doctor", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    faculty = Column(String, nullable=False)
    department = Column(String, nullable=False)
    academic_level = Column(String, nullable=False)
    program = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
    face_profile = relationship("FaceProfile", back_populates="student", uselist=False)
    
    __table_args__ = (
        Index('idx_student_id', 'student_id'),
    )

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    staff_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    faculty = Column(String, nullable=False)
    department = Column(String, nullable=False)
    academic_title = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="doctor")
    courses = relationship("CRN", back_populates="doctor")
    lectures = relationship("Lecture", back_populates="doctor")
    edit_logs = relationship("AttendanceEditLog", back_populates="doctor")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    course_code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    faculty = Column(String, nullable=False)
    department = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    crns = relationship("CRN", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    lectures = relationship("Lecture", back_populates="course")

class CRN(Base):
    __tablename__ = "crns"
    
    id = Column(Integer, primary_key=True, index=True)
    crn = Column(String, unique=True, index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String, nullable=False)
    room = Column(String, nullable=False)
    status = Column(Enum(Status), default=Status.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    course = relationship("Course", back_populates="crns")
    doctor = relationship("Doctor", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="crn")
    lectures = relationship("Lecture", back_populates="crn")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    crn_id = Column(Integer, ForeignKey("crns.id"), nullable=False)
    academic_year = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    crn = relationship("CRN", back_populates="enrollments")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uix_student_course"),
    )

class Lecture(Base):
    __tablename__ = "lectures"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    crn_id = Column(Integer, ForeignKey("crns.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    lecture_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    attendance_open_time = Column(DateTime, nullable=False)
    attendance_close_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    status = Column(Enum(LectureStatus), default=LectureStatus.scheduled)
    cancellation_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    course = relationship("Course", back_populates="lectures")
    crn = relationship("CRN", back_populates="lectures")
    doctor = relationship("Doctor", back_populates="lectures")
    attendance_records = relationship("AttendanceRecord", back_populates="lecture")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    crn_id = Column(Integer, ForeignKey("crns.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    attendance_time = Column(DateTime, nullable=False)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    method = Column(Enum(RecordMethod), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    lecture = relationship("Lecture", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")
    course = relationship("Course")
    crn = relationship("CRN")
    
    # Unique constraint and indexes
    __table_args__ = (
        UniqueConstraint("lecture_id", "student_id", name="uix_lecture_student"),
        Index('idx_attendance_lecture', 'lecture_id'),
        Index('idx_attendance_student', 'student_id'),
        Index('idx_attendance_course', 'course_id'),
    )

class FaceProfile(Base):
    __tablename__ = "face_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    face_embedding = Column(LargeBinary, nullable=False)
    image_reference = Column(String, nullable=True)
    confidence_threshold = Column(Float, default=0.7)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    student = relationship("Student", back_populates="face_profile")

class AttendanceEditLog(Base):
    __tablename__ = "attendance_edit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    attendance_record_id = Column(Integer, ForeignKey("attendance_records.id"), nullable=False)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    old_status = Column(Enum(AttendanceStatus), nullable=False)
    new_status = Column(Enum(AttendanceStatus), nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    lecture = relationship("Lecture")
    student = relationship("Student")
    doctor = relationship("Doctor", back_populates="edit_logs")

# Database setup
from backend.config import settings

# Fail fast if SQLite in production
if os.getenv("ENVIRONMENT", "development") == "production" and settings.DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("SQLite is not supported in production. Please use PostgreSQL.")

# Handle SQLite vs PostgreSQL connection args
connect_args = {}
pool_config = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL connection pooling
    pool_config = {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 3600,   # Recycle connections after 1 hour
    }

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    **pool_config
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        # Test connection
        db.execute("SELECT 1")
        yield db
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Database connection failed: {str(e)}")
    finally:
        db.close()