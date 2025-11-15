"""
Timeline model - represents events in story chronology
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class TimelineEvent(Base):
    """Story timeline event"""

    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Event info
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Timing
    story_date = Column(String(200))  # In-story date/time (flexible format)
    chapter_reference = Column(String(200))  # Which chapter(s) this appears in
    order_index = Column(Integer)  # Chronological order

    # Category
    event_type = Column(String(100))  # historical, plot, character, world

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="timeline_events")

    def __repr__(self):
        return f"<TimelineEvent(id={self.id}, title='{self.title}', date='{self.story_date}')>"
