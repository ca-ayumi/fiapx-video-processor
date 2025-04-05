from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from datetime import datetime

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    status = Column(String, default="processing")
    user_email = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
