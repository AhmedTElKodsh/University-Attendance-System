from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date, time
from typing import Optional, List
from backend.database import UserRole, Status, DayOfWeek, LectureStatus, AttendanceStatus, RecordMethod


# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    status: Status
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Student schemas
class StudentBase(BaseModel):
    student_id: str
    full_name: str
    faculty: str
    department: str
    academic_level: str
    program: str


class StudentCreate(StudentBase):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    academic_level: Optional[str] = None
    program: Optional[str] = None
    status: Optional[Status] = None


class StudentResponse(StudentBase):
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Status
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Doctor schemas
class DoctorBase(BaseModel):
    staff_id: str
    full_name: str
    email: EmailStr
    faculty: str
    department: str
    academic_title: str


class DoctorCreate(DoctorBase):
    phone: Optional[str] = None
    user_id: int


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    academic_title: Optional[str] = None
    status: Optional[Status] = None


class DoctorResponse(DoctorBase):
    id: int
    phone: Optional[str] = None
    user_id: int
    status: Status
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Course schemas
class CourseBase(BaseModel):
    course_name: str
    course_code: str
    faculty: str
    department: str
    academic_year: str
    semester: str


class CourseCreate(CourseBase):
    description: Optional[str] = None


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    description: Optional[str] = None
    faculty: Optional[str] = None
    department: Optional[str] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    status: Optional[Status] = None


class CourseResponse(CourseBase):
    id: int
    description: Optional[str] = None
    status: Status
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# CRN schemas
class CRNBase(BaseModel):
    crn: str
    course_id: int
    doctor_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    location: str
    room: str


class CRNCreate(CRNBase):
    pass


class CRNUpdate(BaseModel):
    doctor_id: Optional[int] = None
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    room: Optional[str] = None
    status: Optional[Status] = None


class CRNResponse(CRNBase):
    id: int
    status: Status
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Enrollment schemas
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
    crn_id: int
    academic_year: str
    semester: str


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    crn_id: int
    academic_year: str
    semester: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Lecture schemas
class LectureBase(BaseModel):
    course_id: int
    crn_id: int
    doctor_id: int
    lecture_date: date
    start_time: time
    end_time: time
    attendance_open_time: datetime
    attendance_close_time: datetime
    location: str


class LectureCreate(LectureBase):
    pass


class LectureUpdate(BaseModel):
    status: Optional[LectureStatus] = None
    cancellation_reason: Optional[str] = None


class LectureResponse(LectureBase):
    id: int
    status: LectureStatus
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Attendance schemas
class AttendanceRecordCreate(BaseModel):
    lecture_id: int
    student_id: int
    course_id: int
    crn_id: int
    status: AttendanceStatus
    attendance_time: datetime
    recorded_by: Optional[int] = None
    method: RecordMethod


class AttendanceRecordResponse(BaseModel):
    id: int
    lecture_id: int
    student_id: int
    course_id: int
    crn_id: int
    status: AttendanceStatus
    attendance_time: datetime
    recorded_by: Optional[int] = None
    method: RecordMethod
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Face Profile schemas
class FaceProfileCreate(BaseModel):
    student_id: int
    face_embedding: bytes
    image_reference: Optional[str] = None
    confidence_threshold: float = 0.6


class FaceProfileResponse(BaseModel):
    id: int
    student_id: int
    image_reference: Optional[str] = None
    confidence_threshold: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Attendance Edit Log schemas
class AttendanceEditLogCreate(BaseModel):
    attendance_record_id: int
    lecture_id: int
    student_id: int
    doctor_id: int
    old_status: AttendanceStatus
    new_status: AttendanceStatus
    reason: str


class AttendanceEditLogResponse(BaseModel):
    id: int
    attendance_record_id: int
    lecture_id: int
    student_id: int
    doctor_id: int
    old_status: AttendanceStatus
    new_status: AttendanceStatus
    reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Attendance screen schemas
class AttendanceScreenResponse(BaseModel):
    lecture_id: int
    course_name: str
    crn: str
    location: str
    room: str
    attendance_open: bool
    time_remaining: Optional[int] = None


# Statistics schemas
class SystemStats(BaseModel):
    total_students: int
    total_doctors: int
    total_courses: int
    total_lectures: int
    total_attendance_records: int


class AttendanceStats(BaseModel):
    lecture_id: int
    course_name: str
    date: date
    present_count: int
    absent_count: int
    total_enrolled: int