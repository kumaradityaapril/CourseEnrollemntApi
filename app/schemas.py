# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import List, Optional

class StudentBase(BaseModel):
    name: str
    email: EmailStr

class StudentCreate(StudentBase):
    pass  # Nothing extra needed for creation

class StudentRead(StudentBase):
    id: int

    class Config:
        orm_mode = True

class FacultyBase(BaseModel):
    name: str
    email: EmailStr

class FacultyCreate(FacultyBase):
    pass

class FacultyRead(FacultyBase):
    id: int

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    name: str
    credits: int = 3

class CourseCreate(CourseBase):
    faculty_id: int

class CourseRead(CourseBase):
    id: int
    faculty_id: int

    class Config:
        orm_mode = True

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentRead(EnrollmentBase):
    id: int
    grade: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for assigning/updating grade
from pydantic import constr

class GradeAssign(BaseModel):
    enrollment_id: int
    grade: constr(strip_whitespace=True, min_length=1, max_length=2)
