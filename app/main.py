from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import courses, enrollments, faculty, students, users
from app.db.init_db import init_db
from app.core.error_handlers import register_error_handlers


app = FastAPI()
init_db()

app.include_router(users.router)
app.include_router(users.auth_router)
app.include_router(students.router)
app.include_router(faculty.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
register_error_handlers(app)

origins = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # Add production frontend URLs when ready
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}
