from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base   # ✅ Use the ONE TRUE Base
from app.config import get_settings

settings = get_settings()

# Create engine
engine = create_engine(settings.DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Only use Base imported from models/base.py
    Base.metadata.create_all(bind=engine)
