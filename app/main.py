from fastapi import FastAPI
from .models import Base
from .database import engine
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, schemas


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.post("/students/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=list[schemas.StudentRead])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students

@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
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
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return None

    # In app/main.py
@app.post("/faculty/", response_model=schemas.FacultyRead)
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(get_db)):
    db_faculty = models.Faculty(name=faculty.name, email=faculty.email)
    db.add(db_faculty)
    db.commit()
    db.refresh(db_faculty)
    return db_faculty

@app.get("/faculty/", response_model=list[schemas.FacultyRead])
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

@app.delete("/faculty/{faculty_id}", status_code=204)
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    db_faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if db_faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db.delete(db_faculty)
    db.commit()

@app.post("/courses/", response_model=schemas.CourseRead)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(
        name=course.name,
        credits=course.credits,
        faculty_id=course.faculty_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=list[schemas.CourseRead])
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
    db_course.name = course.name
    db_course.credits = course.credits
    db_course.faculty_id = course.faculty_id
    db.commit()
    db.refresh(db_course)
    return db_course

@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()

@app.post("/enrollments/", response_model=schemas.EnrollmentRead)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    # Optional: Check that student and course exist first!
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
    return db.query(models.Enrollment).all()

@app.get("/enrollments/{enrollment_id}", response_model=schemas.EnrollmentRead)
def read_enrollment_by_id(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment

@app.put("/enrollments/{enrollment_id}/grade", response_model=schemas.EnrollmentRead)
def update_enrollment_grade(enrollment_id: int, grade: schemas.GradeAssign, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db_enrollment.grade = grade.grade
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@app.delete("/enrollments/{enrollment_id}", status_code=204)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(db_enrollment)
    db.commit()


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

Base.metadata.create_all(bind=engine)
