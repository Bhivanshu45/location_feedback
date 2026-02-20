from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

def utc_now():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), index=True)
    
    # Content
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Location
    location_lat = Column(Float, nullable=False)
    location_long = Column(Float, nullable=False)
    location_name = Column(String(255))
    
    # Metadata
    rating = Column(Integer)  # 1-5
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Processing
    embedding = Column(JSONB, nullable=True)  # Store as JSON array
    category = Column(String(100))
    sentiment = Column(String(50))
    key_insights = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    __table_args__ = (
        Index('idx_location', 'location_lat', 'location_long'),
        Index('idx_created', 'created_at'),
    )

class LocationProfile(Base):
    __tablename__ = "location_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Location
    location_hash = Column(String(255), unique=True, index=True)
    location_lat = Column(Float, nullable=False)
    location_long = Column(Float, nullable=False)
    location_name = Column(String(255))
    
    # Aggregated data
    total_reports = Column(Integer, default=0)
    avg_safety_score = Column(Float, default=0.0)
    trend = Column(String(50))
    
    # Cached analysis
    cached_analysis = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_analysis = Column(DateTime(timezone=True))
