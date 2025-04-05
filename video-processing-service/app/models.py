from sqlalchemy import Column, Integer, String, TIMESTAMP
from .database import Base
from datetime import datetime

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="processing")
    user_email = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
