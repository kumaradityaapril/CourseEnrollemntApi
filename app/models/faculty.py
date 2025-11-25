from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    courses = relationship("Course", back_populates="faculty")

