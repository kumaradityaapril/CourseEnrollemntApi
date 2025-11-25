from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    enrollments = relationship("Enrollment", back_populates="student")

