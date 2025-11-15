"""
Chapter model - represents a chapter in a book project
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Chapter(Base):
    """Book chapter"""

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Chapter info
    title = Column(String(500))
    order_index = Column(Integer, nullable=False)  # Chapter order in book
    word_count = Column(Integer, default=0)

    # Content
    content = Column(Text, default="")  # Markdown content
    summary = Column(Text)  # Brief summary for context

    # Status
    status = Column(String(50), default="draft")  # draft, revision, final
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Notes
    notes = Column(Text)

    # File path
    file_path = Column(String(1000))  # Path to chapter markdown file

    # Relationships
    project = relationship("Project", back_populates="chapters")

    def __repr__(self):
        return f"<Chapter(id={self.id}, title='{self.title}', order={self.order_index})>"

    def update_word_count(self):
        """Calculate word count from content"""
        if self.content:
            self.word_count = len(self.content.split())
        else:
            self.word_count = 0
        self.updated_at = datetime.utcnow()
