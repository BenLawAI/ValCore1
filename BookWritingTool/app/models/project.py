"""
Project model - represents a book writing project
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Project(Base):
    """Book writing project"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    genre = Column(String(100))
    target_word_count = Column(Integer, default=80000)
    current_word_count = Column(Integer, default=0)

    # Status tracking
    status = Column(String(50), default="draft")  # draft, revision, final, published
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)

    # Metadata
    description = Column(Text)
    notes = Column(Text)

    # File paths
    project_folder = Column(String(1000))  # Path to project folder

    # Settings
    auto_save_enabled = Column(Boolean, default=True)
    auto_save_interval = Column(Integer, default=30)  # seconds

    # Relationships
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="project", cascade="all, delete-orphan")
    timeline_events = relationship(
        "TimelineEvent", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', genre='{self.genre}')>"

    def update_word_count(self):
        """Recalculate total word count from all chapters"""
        self.current_word_count = sum(chapter.word_count for chapter in self.chapters)
        self.updated_at = datetime.utcnow()

    def progress_percentage(self) -> float:
        """Calculate writing progress as percentage"""
        if self.target_word_count == 0:
            return 0.0
        return min(100.0, (self.current_word_count / self.target_word_count) * 100)
