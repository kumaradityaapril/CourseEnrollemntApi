from fastapi import FastAPI

from app.api import courses, enrollments, faculty, students, users
from app.db.init_db import init_db

app = FastAPI()
init_db()

app.include_router(users.router)
app.include_router(users.auth_router)
app.include_router(students.router)
app.include_router(faculty.router)
app.include_router(courses.router)
app.include_router(enrollments.router)


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
