from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import Student, get_db
from backend.models import StudentCreate, StudentUpdate, StudentResponse
from backend.routers.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=StudentResponse)
async def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check permissions (admin only)
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create students")
    
    # Check if student_id already exists
    existing = db.query(Student).filter(Student.student_id == student.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    if student.email:
        existing_email = db.query(Student).filter(Student.email == student.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    db_student = Student(
        student_id=student.student_id,
        full_name=student.full_name,
        email=student.email,
        phone=student.phone,
        faculty=student.faculty,
        department=student.department,
        academic_level=student.academic_level,
        program=student.program,
        status="active"
    )
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update students")
    
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete students")
    
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return

@router.get("/", response_model=List[StudentResponse])
async def get_students(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Student).all()