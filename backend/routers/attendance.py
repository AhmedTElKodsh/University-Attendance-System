from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

from backend.database import (
    User, Lecture, AttendanceRecord, FaceProfile, Enrollment, Student,
    get_db, LectureStatus, AttendanceStatus, RecordMethod
)
from backend.models import (
    AttendanceScreenResponse, AttendanceRecordResponse, FaceProfileCreate
)
from backend.routers.auth import get_current_user
from backend.config import settings
from backend.services.simple_face_recognition import SimpleFaceRecognitionService as FaceRecognitionService
from backend.services.liveness import LivenessService
from backend.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["attendance"])


# Get attendance screen data (for classroom device)
@router.get("/screen/{crn_id}", response_model=AttendanceScreenResponse)
async def get_attendance_screen_data(
    crn_id: int,
    db: Session = Depends(get_db)
):
    # Find active lecture for this CRN
    lecture = db.query(Lecture).filter(
        Lecture.crn_id == crn_id,
        Lecture.status == LectureStatus.active
    ).order_by(Lecture.lecture_date.desc()).first()
    
    if not lecture:
        raise HTTPException(status_code=404, detail="No active lecture found for this CRN")
    
    # Get course info
    from backend.database import Course, CRN
    course = db.query(Course).filter(Course.id == lecture.course_id).first()
    crn = db.query(CRN).filter(CRN.id == crn_id).first()
    
    # Check if attendance is within time window
    from datetime import datetime
    now = datetime.utcnow()
    attendance_open = lecture.attendance_open_time <= now <= lecture.attendance_close_time
    
    # Calculate time remaining (in seconds)
    time_remaining = None
    if attendance_open:
        time_remaining = int((lecture.attendance_close_time - now).total_seconds())
    
    return AttendanceScreenResponse(
        lecture_id=lecture.id,
        course_name=course.course_name if course else "Unknown",
        crn=crn.crn if crn else "Unknown",
        location=lecture.location,
        room=crn.room if crn else "Unknown",
        attendance_open=attendance_open,
        time_remaining=time_remaining
    )


# Start attendance session (activate lecture)
@router.put("/session/{lecture_id}/start", status_code=status.HTTP_200_OK)
async def start_attendance_session(
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    # Check if user is the doctor for this lecture or an admin
    if current_user.role.value == "doctor":
        from backend.database import Doctor
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or doctor.id != lecture.doctor_id:
            raise HTTPException(status_code=403, detail="Not authorized to manage this lecture")
    elif current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    lecture.status = LectureStatus.active
    lecture.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Attendance session started"}


# Record attendance via face recognition
@router.post("/record", response_model=dict)
async def record_attendance(
    lecture_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Read and decode image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    # Check liveness
    liveness_service = LivenessService()
    is_live, liveness_message = liveness_service.check_liveness(img)
    if not is_live:
        raise HTTPException(status_code=400, detail=f"Liveness check failed: {liveness_message}")
    
    # Get lecture and validate
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    if lecture.status != LectureStatus.active:
        raise HTTPException(status_code=400, detail="Lecture is not active")
    
    # Get all face profiles for students enrolled in this CRN
    enrollments = db.query(Enrollment).filter(Enrollment.crn_id == lecture.crn_id).all()
    student_ids = [e.student_id for e in enrollments]
    
    face_profiles = db.query(FaceProfile).filter(
        FaceProfile.student_id.in_(student_ids)
    ).all()
    
    if not face_profiles:
        raise HTTPException(status_code=404, detail="No face profiles found for enrolled students")
    
    # Recognize face
    face_service = FaceRecognitionService()
    student_id, confidence = face_service.recognize_face(img, face_profiles)
    
    if not student_id:
        raise HTTPException(status_code=404, detail="Face not recognized")
    
    # Check if already recorded
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.lecture_id == lecture_id,
        AttendanceRecord.student_id == student_id
    ).first()
    
    if existing_record:
        raise HTTPException(status_code=400, detail="Attendance already recorded")
    
    # Record attendance
    service = AttendanceService()
    success, message, record = service.record_attendance(
        lecture_id=lecture_id,
        student_id=student_id,
        status=AttendanceStatus.present,
        method=RecordMethod.face_recognition,
        recorded_by=None,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Get student info
    student = db.query(Student).filter(Student.id == student_id).first()
    
    return {
        "message": "Attendance recorded successfully",
        "student_id": student.student_id if student else "Unknown",
        "student_name": student.full_name if student else "Unknown",
        "confidence": confidence,
        "attendance_time": record.attendance_time.isoformat()
    }


# Register face for a student (admin/doctor function)
@router.post("/face/register/{student_id}", status_code=status.HTTP_201_CREATED)
async def register_face(
    student_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Read and decode image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    # Extract face embedding
    face_service = FaceRecognitionService()
    success, embedding_bytes, message = face_service.register_face(img, student_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Check if face profile already exists
    existing_profile = db.query(FaceProfile).filter(FaceProfile.student_id == student_id).first()
    
    if existing_profile:
        # Update existing profile
        existing_profile.face_embedding = embedding_bytes
        existing_profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        new_profile = FaceProfile(
            student_id=student_id,
            face_embedding=embedding_bytes,
            confidence_threshold=settings.FACE_CONFIDENCE_THRESHOLD
        )
        db.add(new_profile)
    
    db.commit()
    return {"message": "Face registered successfully"}