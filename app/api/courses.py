from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
def read_courses(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = Query(None, description="Filter by course name (partial match)"),
    credits: Optional[int] = Query(None, description="Filter by credit count"),
    faculty_id: Optional[int] = Query(None, description="Filter by faculty ID"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Course)
    if name:
        query = query.filter(models.Course.name.ilike(f"%{name}%"))
    if credits is not None:
        query = query.filter(models.Course.credits == credits)
    if faculty_id is not None:
        query = query.filter(models.Course.faculty_id == faculty_id)
    return query.offset(skip).limit(limit).all()


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


