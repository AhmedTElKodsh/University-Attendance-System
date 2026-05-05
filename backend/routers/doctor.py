from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import (
    User, Doctor, Course, CRN, Lecture, AttendanceRecord, Enrollment, Student,
    get_db, UserRole, LectureStatus, AttendanceStatus
)
from backend.models import (
    LectureResponse, AttendanceRecordResponse, AttendanceStats,
    AttendanceRecordCreate
)
from backend.routers.auth import get_current_user
from backend.services.attendance_service import AttendanceService

router = APIRouter(prefix="/doctor", tags=["doctor"])


async def get_current_doctor_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )
    return current_user


def get_doctor_from_user(user: User, db: Session):
    return db.query(Doctor).filter(Doctor.user_id == user.id).first()


# Get assigned courses for the doctor
@router.get("/courses", response_model=List[dict])
async def get_assigned_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor_user)
):
    doctor = get_doctor_from_user(current_user, db)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    crns = db.query(CRN).filter(CRN.doctor_id == doctor.id, CRN.status == "active").all()
    
    result = []
    for crn in crns:
        course = db.query(Course).filter(Course.id == crn.course_id).first()
        if course:
            result.append({
                "crn_id": crn.id,
                "crn": crn.crn,
                "course_id": course.id,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "day_of_week": crn.day_of_week.value,
                "start_time": crn.start_time.strftime("%H:%M"),
                "end_time": crn.end_time.strftime("%H:%M"),
                "location": crn.location,
                "room": crn.room
            })
    
    return result


# Get lecture details
@router.get("/lectures/{lecture_id}", response_model=dict)
async def get_lecture_details(
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor_user)
):
    doctor = get_doctor_from_user(current_user, db)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    lecture = db.query(Lecture).filter(
        Lecture.id == lecture_id,
        Lecture.doctor_id == doctor.id
    ).first()
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    course = db.query(Course).filter(Course.id == lecture.course_id).first()
    crn = db.query(CRN).filter(CRN.id == lecture.crn_id).first()
    
    # Get attendance records
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.lecture_id == lecture_id
    ).all()
    
    attendance_list = []
    for record in attendance_records:
        student = db.query(Student).filter(Student.id == record.student_id).first()
        if student:
            attendance_list.append({
                "record_id": record.id,
                "student_id": student.student_id,
                "student_name": student.full_name,
                "status": record.status.value,
                "attendance_time": record.attendance_time.isoformat(),
                "method": record.method.value
            })
    
    return {
        "lecture_id": lecture.id,
        "course_name": course.course_name if course else "Unknown",
        "crn": crn.crn if crn else "Unknown",
        "lecture_date": lecture.lecture_date.isoformat(),
        "start_time": lecture.start_time.strftime("%H:%M"),
        "end_time": lecture.end_time.strftime("%H:%M"),
        "location": lecture.location,
        "status": lecture.status.value,
        "attendance_records": attendance_list
    }


# Manual attendance addition
@router.post("/attendance/manual", response_model=AttendanceRecordResponse)
async def add_attendance_manual(
    record: AttendanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor_user)
):
    doctor = get_doctor_from_user(current_user, db)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    service = AttendanceService()
    success, message, attendance_record = service.record_attendance(
        lecture_id=record.lecture_id,
        student_id=record.student_id,
        status=record.status,
        method=record.method,
        recorded_by=current_user.id,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return attendance_record


# Manual attendance removal (set to absent)
@router.put("/attendance/{record_id}/remove", status_code=status.HTTP_200_OK)
async def remove_attendance_manual(
    record_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor_user)
):
    doctor = get_doctor_from_user(current_user, db)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    service = AttendanceService()
    success, message = service.edit_attendance(
        record_id=record_id,
        new_status=AttendanceStatus.absent,
        doctor_id=doctor.id,
        reason=reason,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}


# Cancel lecture
@router.put("/lectures/{lecture_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_lecture(
    lecture_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor_user)
):
    doctor = get_doctor_from_user(current_user, db)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    lecture = db.query(Lecture).filter(
        Lecture.id == lecture_id,
        Lecture.doctor_id == doctor.id
    ).first()
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    lecture.status = LectureStatus.cancelled
    lecture.cancellation_reason = reason
    lecture.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Lecture cancelled successfully"}


# Get attendance statistics
@router.get("/attendance/stats", response_model=List[AttendanceStats])
async def get_attendance_stats(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor_user)
):
    doctor = get_doctor_from_user(current_user, db)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    # Get all lectures for this course taught by this doctor
    lectures = db.query(Lecture).filter(
        Lecture.course_id == course_id,
        Lecture.doctor_id == doctor.id
    ).all()
    
    stats = []
    for lecture in lectures:
        # Count present and absent
        present_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.lecture_id == lecture.id,
            AttendanceRecord.status == AttendanceStatus.present
        ).count()
        
        absent_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.lecture_id == lecture.id,
            AttendanceRecord.status == AttendanceStatus.absent
        ).count()
        
        # Get total enrolled students for this CRN
        total_enrolled = db.query(Enrollment).filter(
            Enrollment.crn_id == lecture.crn_id
        ).count()
        
        course = db.query(Course).filter(Course.id == lecture.course_id).first()
        
        stats.append(AttendanceStats(
            lecture_id=lecture.id,
            course_name=course.course_name if course else "Unknown",
            date=lecture.lecture_date,
            present_count=present_count,
            absent_count=absent_count,
            total_enrolled=total_enrolled
        ))
    
    return stats