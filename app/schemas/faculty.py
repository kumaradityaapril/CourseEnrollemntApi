from pydantic import BaseModel, EmailStr, ConfigDict


class FacultyBase(BaseModel):
    name: str
    email: EmailStr


class FacultyCreate(FacultyBase):
    pass


class FacultyRead(FacultyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

