from enum import Enum
from typing import List, Optional

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


class EnrollmentList(BaseModel):
    total: int
    items: List[EnrollmentRead]


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

