from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import individual models so metadata stays aware of them.
from .user import User  # noqa: F401,E402
from .student import Student  # noqa: F401,E402
from .faculty import Faculty  # noqa: F401,E402
from .course import Course  # noqa: F401,E402
from .enrollment import Enrollment  # noqa: F401,E402

__all__ = ["Base", "User", "Student", "Faculty", "Course", "Enrollment"]

