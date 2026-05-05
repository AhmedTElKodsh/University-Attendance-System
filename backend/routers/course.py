from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import Course, CRN, Lecture, Enrollment, get_db
from backend.models import (
    CourseCreate, CourseUpdate, CourseResponse,
    CRNCreate, CRNUpdate, CRNResponse,
    LectureCreate, LectureResponse
)
from backend.routers.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/courses", tags=["courses"])

# Course endpoints
@router.post("/", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create courses")
    
    existing = db.query(Course).filter(Course.course_code == course.course_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course code already exists")
    
    db_course = Course(
        course_name=course.course_name,
        course_code=course.course_code,
        description=course.description,
        faculty=course.faculty,
        department=course.department,
        academic_year=course.academic_year,
        semester=course.semester,
        status="active"
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update courses")
    
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = course_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/", response_model=List[CourseResponse])
async def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

# CRN endpoints
@router.post("/crns", response_model=CRNResponse)
async def create_crn(
    crn: CRNCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create CRNs")
    
    existing = db.query(CRN).filter(CRN.crn == crn.crn).first()
    if existing:
        raise HTTPException(status_code=400, detail="CRN already exists")
    
    db_crn = CRN(
        crn=crn.crn,
        course_id=crn.course_id,
        doctor_id=crn.doctor_id,
        day_of_week=crn.day_of_week,
        start_time=crn.start_time,
        end_time=crn.end_time,
        location=crn.location,
        room=crn.room,
        status="active"
    )
    db.add(db_crn)
    db.commit()
    db.refresh(db_crn)
    return db_crn

@router.get("/crns", response_model=List[CRNResponse])
async def get_crns(db: Session = Depends(get_db)):
    return db.query(CRN).all()

# Lecture endpoints
@router.post("/lectures", response_model=LectureResponse)
async def schedule_lecture(
    lecture: LectureCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can schedule lectures")
    
    db_lecture = Lecture(
        course_id=lecture.course_id,
        crn_id=lecture.crn_id,
        doctor_id=lecture.doctor_id,
        lecture_date=lecture.lecture_date,
        start_time=lecture.start_time,
        end_time=lecture.end_time,
        attendance_open_time=lecture.attendance_open_time,
        attendance_close_time=lecture.attendance_close_time,
        location=lecture.location,
        status="scheduled"
    )
    db.add(db_lecture)
    db.commit()
    db.refresh(db_lecture)
    return db_lecture

@router.get("/lectures", response_model=List[LectureResponse])
async def get_lectures(db: Session = Depends(get_db)):
    return db.query(Lecture).all()