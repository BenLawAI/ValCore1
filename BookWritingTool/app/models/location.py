"""
Location model - represents a location/place in a book project
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Location(Base):
    """World-building location"""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Basic info
    name = Column(String(255), nullable=False)
    location_type = Column(String(100))  # city, building, region, world, etc.

    # Description
    description = Column(Text)
    climate = Column(String(200))
    culture = Column(Text)

    # Geography
    geography = Column(Text)
    landmarks = Column(Text)

    # Additional properties
    properties = Column(JSON)  # Flexible storage for custom attributes

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="locations")

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', type='{self.location_type}')>"
