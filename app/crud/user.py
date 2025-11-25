from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.utils import commit_and_refresh


def get_user_by_username_or_email(
    db: Session, username: str | None = None, email: str | None = None
) -> models.User | None:
    query = db.query(models.User)
    filters = []
    if username is not None:
        filters.append(models.User.username == username)
    if email is not None:
        filters.append(models.User.email == email)
    if not filters:
        return None
    return query.filter(or_(*filters)).first()


def create_user(db: Session, user: schemas.UserCreate, password_hash: str) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        role=user.role,
        is_active=True,
    )
    db.add(db_user)
    return commit_and_refresh(db, db_user)


def list_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_role(db: Session, user: models.User, new_role: str) -> models.User:
    user.role = new_role
    return commit_and_refresh(db, user)


def set_password(db: Session, user: models.User, password_hash: str) -> models.User:
    user.password_hash = password_hash
    return commit_and_refresh(db, user)


def disable_user(db: Session, user: models.User) -> models.User:
    user.is_active = False
    return commit_and_refresh(db, user)

