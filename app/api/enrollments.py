from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import admin_required
from app.crud import enrollment as enrollment_crud
from app.db.database import get_db

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=schemas.EnrollmentRead)
def create_enrollment(
    enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)
):
    student = db.get(models.Student, enrollment.student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    course = db.get(models.Course, enrollment.course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    exists = enrollment_crud.get_existing_enrollment(
        db, enrollment.student_id, enrollment.course_id
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student is already enrolled in this course",
        )
    return enrollment_crud.create_enrollment(db, enrollment)


@router.get("/", response_model=List[schemas.EnrollmentRead])
def read_enrollments(db: Session = Depends(get_db)):
    return enrollment_crud.list_enrollments(db)


@router.get("/{enrollment_id}", response_model=schemas.EnrollmentRead)
def read_enrollment_by_id(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = enrollment_crud.get_enrollment(db, enrollment_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    return enrollment


@router.get("/filter/", response_model=List[schemas.EnrollmentRead])
def filter_enrollments(
    student_id: int | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    return enrollment_crud.filter_enrollments(db, student_id, course_id)


@router.put("/{enrollment_id}/grade", response_model=schemas.EnrollmentRead)
def update_enrollment_grade(
    enrollment_id: int, grade: schemas.GradeAssign, db: Session = Depends(get_db)
):
    db_enrollment = enrollment_crud.get_enrollment(db, enrollment_id)
    if db_enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    return enrollment_crud.update_grade(db, db_enrollment, grade)


@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = enrollment_crud.get_enrollment(db, enrollment_id)
    if db_enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    enrollment_crud.delete_enrollment(db, db_enrollment)

