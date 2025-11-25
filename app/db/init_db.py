from sqlalchemy import inspect, text

from app.db.database import engine
from app.models import Base


def migrate_database():
    """Add missing columns to existing tables."""
    inspector = inspect(engine)
    try:
        columns = [col["name"] for col in inspector.get_columns("users")]
    except Exception:
        # Users table doesn't exist yet.
        return

    if "is_active" not in columns:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"
                )
            )


def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_database()

