from sqlalchemy.orm import Session


def commit_and_refresh(db: Session, instance):
    """Helper to commit and refresh a SQLAlchemy instance."""
    db.commit()
    db.refresh(instance)
    return instance

