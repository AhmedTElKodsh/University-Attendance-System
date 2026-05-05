from backend.database import (
    Lecture, AttendanceRecord, Enrollment, AttendanceEditLog,
    AttendanceStatus, RecordMethod, LectureStatus
)
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Tuple, Optional


class AttendanceService:
    """Service for attendance business logic"""
    
    def validate_attendance(self, lecture_id: int, student_id: int, db: Session) -> Tuple[bool, str]:
        """
        Validate if a student can record attendance for a lecture.
        Checks: lecture exists and is active, student is enrolled, within time window, no duplicate.
        Returns: (is_valid, message)
        """
        # Check lecture exists and is active
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            return False, "Lecture not found"
        if lecture.status != LectureStatus.active:
            return False, "Lecture is not active"
        
        # Check if within attendance window
        now = datetime.utcnow()
        if now < lecture.attendance_open_time or now > lecture.attendance_close_time:
            return False, "Attendance is not open for this lecture"
        
        # Check student enrollment in the CRN
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.crn_id == lecture.crn_id
        ).first()
        if not enrollment:
            return False, "Student is not enrolled in this course CRN"
        
        # Check for duplicate attendance
        existing_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.lecture_id == lecture_id,
            AttendanceRecord.student_id == student_id
        ).first()
        if existing_record:
            return False, "Attendance already recorded for this lecture"
        
        return True, "Validation successful"
    
    def record_attendance(
        self, 
        lecture_id: int, 
        student_id: int, 
        status: AttendanceStatus, 
        method: RecordMethod, 
        recorded_by: Optional[int], 
        db: Session
    ) -> Tuple[bool, str, Optional[AttendanceRecord]]:
        """
        Record attendance for a student.
        Returns: (success, message, attendance_record)
        """
        # Validate first
        is_valid, message = self.validate_attendance(lecture_id, student_id, db)
        if not is_valid:
            return False, message, None
        
        # Get lecture details
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        
        # Create attendance record
        attendance_record = AttendanceRecord(
            lecture_id=lecture_id,
            student_id=student_id,
            course_id=lecture.course_id,
            crn_id=lecture.crn_id,
            status=status,
            attendance_time=datetime.utcnow(),
            recorded_by=recorded_by,
            method=method
        )
        
        try:
            db.add(attendance_record)
            db.commit()
            db.refresh(attendance_record)
            return True, "Attendance recorded successfully", attendance_record
        except Exception as e:
            db.rollback()
            return False, f"Failed to record attendance: {str(e)}", None
    
    def edit_attendance(
        self,
        record_id: int,
        new_status: AttendanceStatus,
        doctor_id: int,
        reason: str,
        db: Session
    ) -> Tuple[bool, str]:
        """
        Edit an attendance record (doctor only), log the change.
        Returns: (success, message)
        """
        record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if not record:
            return False, "Attendance record not found"
        
        old_status = record.status
        if old_status == new_status:
            return False, "New status is the same as old status"
        
        # Update record
        record.status = new_status
        record.updated_at = datetime.utcnow()
        
        # Log the edit
        edit_log = AttendanceEditLog(
            attendance_record_id=record_id,
            lecture_id=record.lecture_id,
            student_id=record.student_id,
            doctor_id=doctor_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            created_at=datetime.utcnow()
        )
        
        try:
            db.add(edit_log)
            db.commit()
            return True, "Attendance record updated successfully"
        except Exception as e:
            db.rollback()
            return False, f"Failed to update attendance: {str(e)}"
    
    def get_lecture_attendance(self, lecture_id: int, db: Session):
        """Get all attendance records for a lecture"""
        return db.query(AttendanceRecord).filter(
            AttendanceRecord.lecture_id == lecture_id
        ).all()