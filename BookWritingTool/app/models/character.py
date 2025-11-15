"""
Character model - represents a character in a book project
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Character(Base):
    """Book character"""

    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Basic info
    name = Column(String(255), nullable=False)
    role = Column(String(100))  # protagonist, antagonist, supporting, minor

    # Physical description
    appearance = Column(Text)
    age = Column(String(50))
    gender = Column(String(50))

    # Character details
    personality = Column(Text)
    backstory = Column(Text)
    goals = Column(Text)
    fears = Column(Text)
    quirks = Column(Text)

    # Relationships with other characters
    relationships = Column(JSON)  # {character_id: relationship_description}

    # Additional attributes (flexible storage)
    attributes = Column(JSON)  # {eye_color: "blue", hair: "blonde", etc.}

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="characters")

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', role='{self.role}')>"

    def get_attribute(self, key: str, default=None):
        """Get a custom attribute"""
        if not self.attributes:
            return default
        return self.attributes.get(key, default)

    def set_attribute(self, key: str, value):
        """Set a custom attribute"""
        if not self.attributes:
            self.attributes = {}
        self.attributes[key] = value
        self.updated_at = datetime.utcnow()
