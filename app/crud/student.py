from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import commit_and_refresh


def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    return commit_and_refresh(db, db_student)


def list_students(db: Session, skip: int = 0, limit: int = 10) -> list[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()


def get_student(db: Session, student_id: int) -> models.Student | None:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def update_student(
    db: Session, db_student: models.Student, student: schemas.StudentCreate
) -> models.Student:
    db_student.name = student.name
    db_student.email = student.email
    return commit_and_refresh(db, db_student)


def delete_student(db: Session, student: models.Student) -> None:
    db.delete(student)
    db.commit()

