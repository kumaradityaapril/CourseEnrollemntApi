from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    credits = Column(Integer, default=3)
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=False)

    faculty = relationship("Faculty", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")

