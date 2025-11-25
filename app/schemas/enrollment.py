from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentRead(EnrollmentBase):
    id: int
    grade: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


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

