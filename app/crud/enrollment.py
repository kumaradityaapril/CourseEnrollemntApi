from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import commit_and_refresh


def get_enrollment(
    db: Session, enrollment_id: int
) -> models.Enrollment | None:
    return (
        db.query(models.Enrollment)
        .filter(models.Enrollment.id == enrollment_id)
        .first()
    )


def list_enrollments(db: Session) -> list[models.Enrollment]:
    return db.query(models.Enrollment).all()


def filter_enrollments(
    db: Session, student_id: int | None = None, course_id: int | None = None
) -> list[models.Enrollment]:
    query = db.query(models.Enrollment)
    if student_id is not None:
        query = query.filter(models.Enrollment.student_id == student_id)
    if course_id is not None:
        query = query.filter(models.Enrollment.course_id == course_id)
    return query.all()


def get_existing_enrollment(
    db: Session, student_id: int, course_id: int
) -> models.Enrollment | None:
    return (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.student_id == student_id,
            models.Enrollment.course_id == course_id,
        )
        .first()
    )


def create_enrollment(
    db: Session, enrollment: schemas.EnrollmentCreate
) -> models.Enrollment:
    db_enrollment = models.Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
    )
    db.add(db_enrollment)
    return commit_and_refresh(db, db_enrollment)


def update_grade(
    db: Session, db_enrollment: models.Enrollment, grade: schemas.GradeAssign
) -> models.Enrollment:
    db_enrollment.grade = grade.grade
    return commit_and_refresh(db, db_enrollment)


def delete_enrollment(db: Session, db_enrollment: models.Enrollment) -> None:
    db.delete(db_enrollment)
    db.commit()

