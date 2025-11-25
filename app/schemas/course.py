from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    name: str
    credits: int = 3


class CourseCreate(CourseBase):
    faculty_id: int


class CourseRead(CourseBase):
    id: int
    faculty_id: int
    model_config = ConfigDict(from_attributes=True)

