from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    current_role = Column(String(120), nullable=True)
    skills_owned = Column(Text, nullable=True)   # comma-separated
    learning_goal = Column(Text, nullable=True)
    experience_level = Column(String(30), default="beginner")  # beginner/intermediate/advanced
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
