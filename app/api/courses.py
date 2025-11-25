from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.core.security import admin_required
from app.crud import course as course_crud
from app.db.database import get_db

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=schemas.CourseRead)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    faculty = db.get(models.Faculty, course.faculty_id)
    if faculty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found"
        )
    return course_crud.create_course(db, course)


@router.get("/", response_model=List[schemas.CourseRead])
def read_courses(db: Session = Depends(get_db)):
    return course_crud.list_courses(db)


@router.get("/{course_id}", response_model=schemas.CourseRead)
def read_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = course_crud.get_course(db, course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


@router.put("/{course_id}", response_model=schemas.CourseRead)
def update_course(
    course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)
):
    db_course = course_crud.get_course(db, course_id)
    if db_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    faculty = db.get(models.Faculty, course.faculty_id)
    if faculty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found"
        )
    return course_crud.update_course(db, db_course, course)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = course_crud.get_course(db, course_id)
    if db_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    course_crud.delete_course(db, db_course)


@router.get("/filter/", response_model=List[schemas.CourseRead])
def filter_courses(faculty_id: int | None = None, db: Session = Depends(get_db)):
    return course_crud.filter_courses(db, faculty_id)

