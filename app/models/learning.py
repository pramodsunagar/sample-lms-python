from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.database.db import Base


class SavedPath(Base):
    __tablename__ = "saved_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    role = Column(String(120), nullable=True)
    target_skill = Column(String(120), nullable=True)
    courses = Column(JSON, nullable=False)   # list of CourseResult dicts
    ai_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CourseProgress(Base):
    __tablename__ = "course_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    saved_path_id = Column(Integer, nullable=True)
    course_url = Column(String(500), nullable=False)
    course_title = Column(String(255), nullable=True)
    status = Column(String(20), default="not_started")  # not_started / in_progress / completed
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PathRemovalLog(Base):
    __tablename__ = "path_removal_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    path_title = Column(String, nullable=False)
    removal_reason = Column(Text, nullable=True)
    removed_at = Column(DateTime, default=datetime.utcnow)
