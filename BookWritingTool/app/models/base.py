"""
Database base configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from typing import Optional

Base = declarative_base()


class Database:
    """Database manager for BookWritingTool"""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection

        Args:
            db_path: Path to SQLite database file. If None, uses in-memory DB for testing.
        """
        if db_path:
            self.db_path = db_path
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{self.db_path}"
        else:
            db_url = "sqlite:///:memory:"

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def drop_all(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
