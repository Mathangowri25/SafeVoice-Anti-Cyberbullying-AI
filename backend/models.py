from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"

    id          = Column(Integer, primary_key=True, index=True)
    text        = Column(String)
    platform    = Column(String, default="unknown")
    user_id     = Column(String, default="anonymous")
    context_id  = Column(String, default="")
    label       = Column(String)
    severity    = Column(Integer)
    confidence  = Column(Float)
    alert_sent  = Column(Boolean, default=False)
    reviewed    = Column(Boolean, default=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)