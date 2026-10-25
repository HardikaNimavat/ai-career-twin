from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.models.user import User
    from backend.app.models.profile import UserProfile
    from backend.app.models.interview import InterviewSession
    from backend.app.models.roadmap import UserRoadmap
    from backend.app.models.exam import ExamSession, SkillHistory
    Base.metadata.create_all(bind=engine)
