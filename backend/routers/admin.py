from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import (
    User, Doctor, Course, CRN, Lecture, Enrollment, AttendanceRecord, get_db,
    UserRole, Status, LectureStatus
)
from backend.models import SystemStats, EnrollmentCreate, EnrollmentResponse
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this endpoint"
        )
    return current_user

# Enrollment Management
@router.post("/enrollments", response_model=EnrollmentResponse)
async def assign_student_to_crn(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if student exists
    from backend.database import Student
    student = db.query(Student).filter(Student.id == enrollment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if CRN exists
    crn = db.query(CRN).filter(CRN.id == enrollment.crn_id).first()
    if not crn:
        raise HTTPException(status_code=404, detail="CRN not found")
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.course_id == enrollment.course_id
    ).first()
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course")
    
    db_enrollment = Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        crn_id=enrollment.crn_id,
        academic_year=enrollment.academic_year,
        semester=enrollment.semester
    )
    
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

# System Statistics
@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    total_students = db.query(Student).count()
    total_doctors = db.query(Doctor).count()
    total_courses = db.query(Course).count()
    total_lectures = db.query(Lecture).count()
    total_attendance_records = db.query(AttendanceRecord).count()
    
    return SystemStats(
        total_students=total_students,
        total_doctors=total_doctors,
        total_courses=total_courses,
        total_lectures=total_lectures,
        total_attendance_records=total_attendance_records
    )