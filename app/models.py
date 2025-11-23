from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ----------------------
# User model for Auth/Role
# ----------------------
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "admin", "faculty", "student"

# ----------------------
# Student Model
# ----------------------
class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    enrollments = relationship("Enrollment", back_populates="student")

# ----------------------
# Faculty Model
# ----------------------
class Faculty(Base):
    __tablename__ = 'faculties'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    courses = relationship("Course", back_populates="faculty")

# ----------------------
# Course Model
# ----------------------
class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    credits = Column(Integer, default=3)
    faculty_id = Column(Integer, ForeignKey('faculties.id'), nullable=False)
    faculty = relationship("Faculty", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")

# ----------------------
# Enrollment Model (Association - Many-to-Many)
# ----------------------
class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    grade = Column(String, nullable=True)
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
