from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import commit_and_refresh


def create_faculty(db: Session, faculty: schemas.FacultyCreate) -> models.Faculty:
    db_faculty = models.Faculty(name=faculty.name, email=faculty.email)
    db.add(db_faculty)
    return commit_and_refresh(db, db_faculty)


def list_faculty(db: Session) -> list[models.Faculty]:
    return db.query(models.Faculty).all()


def get_faculty(db: Session, faculty_id: int) -> models.Faculty | None:
    return db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()


def update_faculty(
    db: Session, db_faculty: models.Faculty, faculty: schemas.FacultyCreate
) -> models.Faculty:
    db_faculty.name = faculty.name
    db_faculty.email = faculty.email
    return commit_and_refresh(db, db_faculty)


def delete_faculty(db: Session, db_faculty: models.Faculty) -> None:
    db.delete(db_faculty)
    db.commit()

