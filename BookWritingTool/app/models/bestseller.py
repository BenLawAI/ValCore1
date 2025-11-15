"""
Bestseller model - tracks bestseller list data
"""
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from datetime import datetime
from .base import Base


class Bestseller(Base):
    """Bestseller tracking data"""

    __tablename__ = "bestsellers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Scraping metadata
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    source = Column(String(50), nullable=False)  # amazon, nyt, usatoday
    genre = Column(String(100))  # thriller, fantasy, overall, etc.

    # Ranking
    rank = Column(Integer, nullable=False)

    # Book info
    title = Column(String(500), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20))

    # Tracking
    weeks_on_list = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    peak_rank = Column(Integer)

    __table_args__ = (
        UniqueConstraint("source", "genre", "title", "author", "scraped_at", name="uix_bestseller"),
    )

    def __repr__(self):
        return f"<Bestseller(rank={self.rank}, title='{self.title}', author='{self.author}', source='{self.source}')>"

    def is_trending(self) -> bool:
        """Check if book has been on list for 3+ consecutive weeks"""
        return self.weeks_on_list >= 3
