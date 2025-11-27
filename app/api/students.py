from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.models.student import Student
from app.core.security import admin_required
from app.crud import student as student_crud
from app.db.database import get_db

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED
)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return student_crud.create_student(db, student)


@router.get("/", response_model=schemas.StudentList)
def read_students(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = Query(
        None, description="Filter by name (partial match)"
    ),
    email: Optional[str] = Query(
        None, description="Filter by email (partial match)"
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Student)
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Student.email.ilike(f"%{email}%"))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{student_id}", response_model=schemas.StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    return student


@router.put("/{student_id}", response_model=schemas.StudentRead)
def update_student(
    student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)
):
    db_student = student_crud.get_student(db, student_id)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    return student_crud.update_student(db, db_student, student)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = student_crud.get_student(db, student_id)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    student_crud.delete_student(db, db_student)


@router.get("/{student_id}/grades/")
def get_student_grades(student_id: int, db: Session = Depends(get_db)):
    enrollments = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.student_id == student_id)
        .all()
    )
    return [
        {
            "course_id": e.course_id,
            "course_name": (
                db.get(models.Course, e.course_id).name if e.course_id else None
            ),
            "grade": e.grade,
        }
        for e in enrollments
    ]

