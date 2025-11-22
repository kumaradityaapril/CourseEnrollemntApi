from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

# Student schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int
    class Config:
        from_attributes = True

# Faculty schemas
class FacultyBase(BaseModel):
    name: str
    email: EmailStr

class FacultyCreate(FacultyBase):
    pass

class FacultyRead(FacultyBase):
    id: int
    class Config:
        from_attributes = True

# Course schemas
class CourseBase(BaseModel):
    name: str
    credits: int = 3

class CourseCreate(CourseBase):
    faculty_id: int

class CourseRead(CourseBase):
    id: int
    faculty_id: int
    class Config:
        from_attributes = True

# Enrollment schemas
class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentRead(EnrollmentBase):
    id: int
    grade: Optional[str] = None
    class Config:
        from_attributes = True

# Enum and schema for assigning/updating grade
class GradeEnum(str, Enum):
    A = "A"
    A_minus = "A-"
    B = "B"
    B_minus = "B-"
    C = "C"
    D = "D"
    F = "F"

class GradeAssign(BaseModel):
    grade: GradeEnum
