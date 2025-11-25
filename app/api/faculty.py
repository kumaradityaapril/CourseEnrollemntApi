from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.core.security import admin_required
from app.crud import faculty as faculty_crud
from app.db.database import get_db

router = APIRouter(prefix="/faculty", tags=["Faculty"])


@router.post("/", response_model=schemas.FacultyRead)
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    return faculty_crud.create_faculty(db, faculty)


@router.get("/", response_model=List[schemas.FacultyRead])
def read_faculty(db: Session = Depends(get_db)):
    return faculty_crud.list_faculty(db)


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

