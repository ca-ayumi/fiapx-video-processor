import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/videodb")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
