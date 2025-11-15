"""
LLM Usage model - tracks API usage and costs
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime
from .base import Base


class LLMUsage(Base):
    """LLM API usage tracking"""

    __tablename__ = "llm_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Provider info
    provider = Column(String(50), nullable=False)  # claude, gpt, ollama
    mode = Column(String(20), nullable=False)  # online, offline
    model = Column(String(100), nullable=False)  # claude-sonnet-4.5, gpt-4-turbo, etc.

    # Token usage
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)

    # Cost (in USD)
    cost_usd = Column(Numeric(10, 4), default=0.0000)  # Offline = $0.00

    # Context
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    purpose = Column(String(200))  # generation, style_analysis, etc.

    def __repr__(self):
        return f"<LLMUsage(provider='{self.provider}', model='{self.model}', cost=${self.cost_usd})>"

    @property
    def total_tokens(self) -> int:
        """Get total token count"""
        return self.input_tokens + self.output_tokens
