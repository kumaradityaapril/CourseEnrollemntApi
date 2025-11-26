from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import (
    admin_required,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.crud import user as user_crud
from app.db.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(tags=["Auth"])


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (admin, faculty, or student).
    """
    if user_crud.get_user_by_username_or_email(db, user.username, user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists.",
        )
    hashed_pw = get_password_hash(user.password)
    return user_crud.create_user(db, user, hashed_pw)


@auth_router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    User login (returns JWT access token).
    """
    user = user_crud.get_user_by_username_or_email(db, username=form_data.username)
    if (
        not user
        or not user.is_active
        or not verify_password(form_data.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password, or account disabled.",
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/", response_model=List[schemas.UserRead], dependencies=[Depends(admin_required)]
)
def list_users(db: Session = Depends(get_db)):
    """List all registered users (admin only)."""
    return user_crud.list_users(db)


@router.get(
    "/{user_id}",
    response_model=schemas.UserRead,
    dependencies=[Depends(admin_required)],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get details of a specific user (admin only)."""
    user = user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch(
    "/{user_id}/role",
    response_model=schemas.UserRead,
    dependencies=[Depends(admin_required)],
)
def update_user_role(
    user_id: int, role_update: schemas.RoleUpdate, db: Session = Depends(get_db)
):
    """Update a user's role (admin only)."""
    user = user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_crud.update_role(db, user, role_update.role)


@router.post("/{user_id}/change-password")
def change_password(
    user_id: int,
    data: schemas.PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Change your password (requires old password).
    Admin can change any user's password.
    """
    user = user_crud.get_user(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or disabled.",
        )
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: you can't change this user's password.",
        )
    if current_user.role != "admin":
        if not verify_password(data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect.",
            )
    new_hashed = get_password_hash(data.new_password)
    user_crud.set_password(db, user, new_hashed)
    return {"detail": "Password changed successfully."}


@router.patch("/{user_id}", response_model=schemas.UserRead)
def update_user_profile(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update user profile (username and/or email). Users can update their own profile, admins can update any profile."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update profile",
        )
    if user_update.email and user_update.email != user.email:
        if db.query(models.User).filter(models.User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
            )
        user.email = user_update.email
    if user_update.username and user_update.username != user.username:
        if (
            db.query(models.User)
            .filter(models.User.username == user_update.username)
            .first()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already in use"
            )
        user.username = user_update.username
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/{user_id}/disable",
    dependencies=[Depends(admin_required)],
)
def disable_user(user_id: int, db: Session = Depends(get_db)):
    """
    Admin disables (soft deletes) a user, making them unable to log in or use the API.
    """
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user_crud.disable_user(db, user)
    return {"detail": f"User {user.username} disabled."}


@router.post(
    "/{user_id}/enable",
    response_model=schemas.UserRead,
    dependencies=[Depends(admin_required)],
)
def enable_user(user_id: int, db: Session = Depends(get_db)):
    """
    Admin enables a user, allowing them to log in and use the API again.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active"
        )
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

