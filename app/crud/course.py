from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import commit_and_refresh


def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(
        name=course.name,
        credits=course.credits,
        faculty_id=course.faculty_id,
    )
    db.add(db_course)
    return commit_and_refresh(db, db_course)


def list_courses(db: Session) -> list[models.Course]:
    return db.query(models.Course).all()


def get_course(db: Session, course_id: int) -> models.Course | None:
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def filter_courses(db: Session, faculty_id: int | None = None) -> list[models.Course]:
    query = db.query(models.Course)
    if faculty_id is not None:
        query = query.filter(models.Course.faculty_id == faculty_id)
    return query.all()


def update_course(
    db: Session, db_course: models.Course, course: schemas.CourseCreate
) -> models.Course:
    db_course.name = course.name
    db_course.credits = course.credits
    db_course.faculty_id = course.faculty_id
    return commit_and_refresh(db, db_course)


def delete_course(db: Session, db_course: models.Course) -> None:
    db.delete(db_course)
    db.commit()

