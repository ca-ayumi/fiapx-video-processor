from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False, default='processing')
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
