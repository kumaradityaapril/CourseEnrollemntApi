from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas
from app.models.faculty import Faculty
from app.core.security import admin_required
from app.crud import faculty as faculty_crud
from app.db.database import get_db

router = APIRouter(prefix="/faculty", tags=["Faculty"])


@router.post("/", response_model=schemas.FacultyRead)
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    return faculty_crud.create_faculty(db, faculty)


@router.get("/", response_model=List[schemas.FacultyRead])
def read_faculty(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    email: Optional[str] = Query(None, description="Filter by email (partial match)"),
    db: Session = Depends(get_db),
):
    query = db.query(Faculty)
    if name:
        query = query.filter(Faculty.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Faculty.email.ilike(f"%{email}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{faculty_id}", response_model=schemas.FacultyRead)
def read_faculty_by_id(faculty_id: int, db: Session = Depends(get_db)):
    faculty = faculty_crud.get_faculty(db, faculty_id)
    if faculty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found"
        )
    return faculty


@router.put("/{faculty_id}", response_model=schemas.FacultyRead)
def update_faculty(
    faculty_id: int, faculty: schemas.FacultyCreate, db: Session = Depends(get_db)
):
    db_faculty = faculty_crud.get_faculty(db, faculty_id)
    if db_faculty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found"
        )
    return faculty_crud.update_faculty(db, db_faculty, faculty)


@router.delete(
    "/{faculty_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    db_faculty = faculty_crud.get_faculty(db, faculty_id)
    if db_faculty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found"
        )
    faculty_crud.delete_faculty(db, db_faculty)

