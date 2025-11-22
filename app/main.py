from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import Base
from .database import engine, SessionLocal
from . import models, schemas

app = FastAPI()

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------
# Student CRUD Endpoints
# -----------------------

@app.post("/students/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student.
    - **name**: Full name of the student
    - **email**: Unique, valid email address
    """
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=list[schemas.StudentRead])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a list of all students (paginated).
    """
    return db.query(models.Student).offset(skip).limit(limit).all()

@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    """
    Get a specific student by ID.
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Update a specific student's details.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db_student.name = student.name
    db_student.email = student.email
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Delete a student by ID.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return None

# ----------------------
# Faculty CRUD Endpoints
# ----------------------

@app.post("/faculty/", response_model=schemas.FacultyRead)
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    """
    Create a new faculty member.
    """
    db_faculty = models.Faculty(name=faculty.name, email=faculty.email)
    db.add(db_faculty)
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.get("/faculty/", response_model=list[schemas.FacultyRead])
def read_faculty(db: Session = Depends(get_db)):
    """
    Get a list of all faculty.
    """
    return db.query(models.Faculty).all()

@app.get("/faculty/{faculty_id}", response_model=schemas.FacultyRead)
def read_faculty_by_id(faculty_id: int, db: Session = Depends(get_db)):
    """
    Get a specific faculty by ID.
    """
    faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty

@app.put("/faculty/{faculty_id}", response_model=schemas.FacultyRead)
def update_faculty(faculty_id: int, faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    """
    Update a specific faculty's details.
    """
    db_faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if db_faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db_faculty.name = faculty.name
    db_faculty.email = faculty.email
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.delete("/faculty/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    """
    Delete a faculty member by ID.
    """
    db_faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if db_faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db.delete(db_faculty)
    db.commit()
    return None

# --------------------
# Course CRUD Endpoints
# --------------------

@app.post("/courses/", response_model=schemas.CourseRead)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """
    Create a new course (faculty_id must exist).
    """
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

@app.get("/courses/", response_model=list[schemas.CourseRead])
def read_courses(db: Session = Depends(get_db)):
    """
    Get a list of all courses.
    """
    return db.query(models.Course).all()

@app.get("/courses/{course_id}", response_model=schemas.CourseRead)
def read_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """
    Get a specific course by ID.
    """
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put("/courses/{course_id}", response_model=schemas.CourseRead)
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """
    Update a specific course's details.
    """
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    # Validate faculty
    faculty = db.query(models.Faculty).filter(models.Faculty.id == course.faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db_course.name = course.name
    db_course.credits = course.credits
    db_course.faculty_id = course.faculty_id
    db.commit()
    db.refresh(db_course)
    return db_course

@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Delete a course by ID.
    """
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return None

# ------------------------
# Enrollment CRUD Endpoints
# ------------------------

@app.post("/enrollments/", response_model=schemas.EnrollmentRead)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    """
    Enroll a student in a course.
    - Validates student and course existence.
    - Prevents duplicate enrollment.
    """
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

@app.get("/enrollments/", response_model=list[schemas.EnrollmentRead])
def read_enrollments(db: Session = Depends(get_db)):
    """
    Get a list of all enrollments.
    """
    return db.query(models.Enrollment).all()

@app.get("/enrollments/{enrollment_id}", response_model=schemas.EnrollmentRead)
def read_enrollment_by_id(enrollment_id: int, db: Session = Depends(get_db)):
    """
    Get a specific enrollment by ID.
    """
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment

@app.put("/enrollments/{enrollment_id}/grade", response_model=schemas.EnrollmentRead)
def update_enrollment_grade(enrollment_id: int, grade: schemas.GradeAssign, db: Session = Depends(get_db)):
    """
    Assign or update the grade for a student's enrollment.
    """
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db_enrollment.grade = grade.grade
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@app.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """
    Remove a student from a course (delete an enrollment).
    """
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(db_enrollment)
    db.commit()
    return None

# --------------
# Root Endpoint
# --------------

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
