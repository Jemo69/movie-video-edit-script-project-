from sqlalchemy import Column, Integer, String, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(Text)

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_name = Column(String, index=True)
    project_link = Column(Text)

    def __repr__(self):
        return f"<Video(video_name={self.video_name})>"