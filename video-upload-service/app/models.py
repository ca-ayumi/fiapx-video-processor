from sqlalchemy import Column, Integer, String
from .database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    user_email = Column(String, index=True)
    status = Column(String, default="processing")
