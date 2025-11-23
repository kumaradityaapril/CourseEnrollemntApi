from pydantic import BaseModel, EmailStr, ConfigDict, constr, Field
from typing import List, Optional
from enum import Enum

# Student schemas
class StudentBase(BaseModel):
    name: str = Field(..., description="Full name of the student")
    email: EmailStr = Field(..., description="Unique student email address")

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Faculty schemas
class FacultyBase(BaseModel):
    name: str
    email: EmailStr

class FacultyCreate(FacultyBase):
    pass

class FacultyRead(FacultyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Course schemas
class CourseBase(BaseModel):
    name: str
    credits: int = 3

class CourseCreate(CourseBase):
    faculty_id: int

class CourseRead(CourseBase):
    id: int
    faculty_id: int
    model_config = ConfigDict(from_attributes=True)

# Enrollment schemas
class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentRead(EnrollmentBase):
    id: int
    grade: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

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

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: constr(min_length=6, max_length=72)

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Password change schema (standalone, not nested)
class PasswordChangeRequest(BaseModel):
    old_password: constr(min_length=6, max_length=72)
    new_password: constr(min_length=6, max_length=72)
