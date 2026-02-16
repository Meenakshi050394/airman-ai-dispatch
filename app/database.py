from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import Base
from app.config import settings
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
