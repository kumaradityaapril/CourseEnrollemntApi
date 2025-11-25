from pydantic import BaseModel, EmailStr, ConfigDict, Field


class StudentBase(BaseModel):
    name: str = Field(..., description="Full name of the student")
    email: EmailStr = Field(..., description="Unique student email address")


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

