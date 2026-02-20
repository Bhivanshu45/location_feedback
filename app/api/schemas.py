from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Dict, Optional

# ==================== Location ====================

class LocationInput(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    long: float = Field(..., ge=-180, le=180, description="Longitude")
    name: Optional[str] = None

# ==================== Feedback Request/Response ====================

class SingleFeedback(BaseModel):
    """Single Q&A pair"""
    question: str = Field(..., min_length=10, max_length=500, description="Safety question")
    answer: str = Field(..., min_length=20, max_length=2000, description="User feedback")
    rating: int = Field(..., ge=1, le=10, description="Safety rating 1-10")

    @validator('question')
    def validate_question(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Question must be at least 10 characters")
        return v.strip()

    @validator('answer')
    def validate_answer(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError("Answer must be at least 20 characters")
        return v.strip()


class FeedbackSubmitRequest(BaseModel):
    """Multiple Q&A for single location"""
    location: LocationInput
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    feedbacks: List[SingleFeedback] = Field(..., min_items=1, max_items=10, description="1-10 Q&A pairs")

    @validator('feedbacks')
    def validate_feedbacks(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least 1 feedback required")
        if len(v) > 10:
            raise ValueError("Maximum 10 feedbacks per request")
        return v


class FeedbackSubmitResponse(BaseModel):
    success: bool
    feedback_ids: List[str] = Field(..., description="List of feedback IDs")
    count: int = Field(..., description="Number of feedbacks submitted")
    message: str
    processing_status: str


# ==================== Analysis Request/Response ====================

class TimeBasedSafety(BaseModel):
    morning: str = "Unknown"
    afternoon: str = "Unknown"
    evening: str = "Unknown"
    night: str = "Unknown"


class SafetyProfile(BaseModel):
    score: float = Field(..., ge=0, le=10, description="Safety score 0-10")
    trend: str = Field(..., description="Trend: improving, stable, declining")
    confidence: float = Field(..., ge=0, le=1, description="Confidence 0-1")
    status: str = Field(..., description="Safe, Moderate, Caution, or Unknown")
    color: str = Field(..., description="green, yellow, orange, red, or gray")


class SafetyConcern(BaseModel):
    concern: str
    severity: str  # high, medium, low
    frequency: str  # rare, occasional, common
    

class Concern(BaseModel):
    title: str
    severity: str


class LocationInsights(BaseModel):
    top_concerns: List[Concern] = Field(..., max_items=5)
    positive_aspects: List[str] = Field(..., max_items=5)
    time_patterns: TimeBasedSafety
    recommendations: List[str] = Field(..., max_items=5)
    key_findings: str = Field(..., description="Summary of key findings")


class DataQuality(BaseModel):
    reports_count: int
    date_range: str
    last_updated: str
    data_freshness_hours: int
    data_freshness_status: str  # "Fresh", "Recent", "Outdated"


class LocationAnalysisResponse(BaseModel):
    location: LocationInput
    unsafe_probability: float = Field(..., ge=0, le=1, description="Unsafe probability 0-1 scale")
    status: str = Field(..., description="Safe, Moderate, Caution, or Not Safe")
    color: str = Field(..., description="green, yellow, orange, red, or gray")
    trend: str = Field(..., description="improving, stable, or declining")
    top_concerns: List[Concern] = Field(..., max_items=5)
    recommendations: List[str] = Field(..., max_items=5)
    reports_count: int = Field(..., description="Number of feedback reports analyzed")
    summary: str = Field(..., description="Brief analysis summary")


class LocationAnalysisRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    long: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None
