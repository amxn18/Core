from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from .base import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    latency_ms = Column(Float, nullable=False)
    prediction = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    status = Column(String, nullable=False)
