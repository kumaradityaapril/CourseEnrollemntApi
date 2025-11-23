from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import Base
from .database import engine, SessionLocal
from . import models, schemas

from passlib.context import CryptContext
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import List

app = FastAPI()
Base.metadata.create_all(bind=engine)

# ====== Security Setup ======
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    _ = pwd_context.hash("test")
    USE_PASSLIB = True
except Exception:
    USE_PASSLIB = False
    pwd_context = None

SECRET_KEY = "your_random_secret_key_123"  # Change to a secure value in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_password_hash(password: str):
    password_bytes = password.encode('utf-8')[:72]
    password = password_bytes.decode('utf-8', errors='ignore')
    if not USE_PASSLIB:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode('utf-8')
    try:
        return pwd_context.hash(password)
    except Exception:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    pw = plain_password.encode('utf-8')[:72]
    pw = pw.decode('utf-8', errors='ignore')
    if not USE_PASSLIB:
        return bcrypt.checkpw(pw.encode(), hashed_password.encode())
    try:
        return pwd_context.verify(pw, hashed_password)
    except Exception:
        return bcrypt.checkpw(pw.encode(), hashed_password.encode())

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: SessionLocal())):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def admin_required(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====== User Authentication ======
@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (admin, faculty, or student).
    """
    if db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first():
        raise HTTPException(status_code=409, detail="Username or email already exists.")
    hashed_pw = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login (returns JWT access token).
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ====== Day 13: User Management (Admin only) ======
@app.get("/users/", response_model=List[schemas.UserRead], dependencies=[Depends(admin_required)])
def list_users(db: Session = Depends(get_db)):
    """
    List all registered users (admin only).
    """
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(admin_required)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific user (admin only).
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

from pydantic import BaseModel

class RoleUpdate(BaseModel):
    role: str

@app.patch("/users/{user_id}/role", response_model=schemas.UserRead, dependencies=[Depends(admin_required)])
def update_user_role(user_id: int, role_update: RoleUpdate, db: Session = Depends(get_db)):
    """
    Update a user's role (admin only).
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

# ========== Student CRUD ==========
@app.post("/students/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student record.
    """
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[schemas.StudentRead])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    List all students (paginated).
    """
    return db.query(models.Student).offset(skip).limit(limit).all()

@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    """
    Get a student by their ID.
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Update an existing student's information.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db_student.name = student.name
    db_student.email = student.email
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Delete a student (admin only).
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return None

@app.get("/students/{student_id}/grades/")
def get_student_grades(student_id: int, db: Session = Depends(get_db)):
    """
    Get all enrollments and grades for a student.
    """
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).all()
    return [
        {
            "course_id": e.course_id,
            "course_name": db.query(models.Course).filter(models.Course.id == e.course_id).first().name if e.course_id else None,
            "grade": e.grade
        }
        for e in enrollments
    ]

# ========== Faculty CRUD ==========
@app.post("/faculty/", response_model=schemas.FacultyRead)
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    db_faculty = models.Faculty(name=faculty.name, email=faculty.email)
    db.add(db_faculty)
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.get("/faculty/", response_model=List[schemas.FacultyRead])
def read_faculty(db: Session = Depends(get_db)):
    return db.query(models.Faculty).all()

@app.get("/faculty/{faculty_id}", response_model=schemas.FacultyRead)
def read_faculty_by_id(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty

@app.put("/faculty/{faculty_id}", response_model=schemas.FacultyRead)
def update_faculty(faculty_id: int, faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    db_faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if db_faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db_faculty.name = faculty.name
    db_faculty.email = faculty.email
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.delete("/faculty/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    db_faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if db_faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db.delete(db_faculty)
    db.commit()
    return None

# ========== Course CRUD ==========
@app.post("/courses/", response_model=schemas.CourseRead)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == course.faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db_course = models.Course(
        name=course.name,
        credits=course.credits,
        faculty_id=course.faculty_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=List[schemas.CourseRead])
def read_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.get("/courses/{course_id}", response_model=schemas.CourseRead)
def read_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put("/courses/{course_id}", response_model=schemas.CourseRead)
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    faculty = db.query(models.Faculty).filter(models.Faculty.id == course.faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db_course.name = course.name
    db_course.credits = course.credits
    db_course.faculty_id = course.faculty_id
    db.commit()
    db.refresh(db_course)
    return db_course

@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return None

@app.get("/courses/filter/", response_model=List[schemas.CourseRead])
def filter_courses(faculty_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Course)
    if faculty_id:
        query = query.filter(models.Course.faculty_id == faculty_id)
    return query.all()

# ========== Enrollment CRUD ==========
@app.post("/enrollments/", response_model=schemas.EnrollmentRead)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == enrollment.student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    course = db.query(models.Course).filter(models.Course.id == enrollment.course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    exists = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == enrollment.student_id,
        models.Enrollment.course_id == enrollment.course_id
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student is already enrolled in this course"
        )
    db_enrollment = models.Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@app.get("/enrollments/", response_model=List[schemas.EnrollmentRead])
def read_enrollments(db: Session = Depends(get_db)):
    return db.query(models.Enrollment).all()

@app.get("/enrollments/{enrollment_id}", response_model=schemas.EnrollmentRead)
def read_enrollment_by_id(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment

@app.get("/enrollments/filter/", response_model=List[schemas.EnrollmentRead])
def filter_enrollments(student_id: int = None, course_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Enrollment)
    if student_id:
        query = query.filter(models.Enrollment.student_id == student_id)
    if course_id:
        query = query.filter(models.Enrollment.course_id == course_id)
    return query.all()

@app.put("/enrollments/{enrollment_id}/grade", response_model=schemas.EnrollmentRead)
def update_enrollment_grade(enrollment_id: int, grade: schemas.GradeAssign, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db_enrollment.grade = grade.grade
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@app.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(db_enrollment)
    db.commit()
    return None

# ===== Root endpoint =====
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
