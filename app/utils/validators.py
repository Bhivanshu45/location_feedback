from datetime import datetime, timedelta, timezone
from app.utils.logger import get_logger

logger = get_logger(__name__)

def validate_timestamp(timestamp: datetime) -> bool:
    """Validate feedback timestamp is reasonable"""
    # Accept any timestamp within 5 years
    # Users can submit feedback from past events
    now = datetime.now(timezone.utc)
    five_years_ago = now - timedelta(days=365*5)
    
    # Make timestamp aware if it's naive
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    # Only reject if VERY old (more than 5 years)
    if timestamp < five_years_ago:
        raise ValueError("Feedback too old (max 5 years)")
    
    return True

def validate_coordinates(lat: float, long: float) -> bool:
    """Validate location coordinates"""
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90")
    if not (-180 <= long <= 180):
        raise ValueError(f"Invalid longitude: {long}. Must be between -180 and 180")
    return True

def validate_rating(rating: int) -> bool:
    """Validate safety rating"""
    if not (1 <= rating <= 10):
        raise ValueError(f"Invalid rating: {rating}. Must be between 1 and 10")
    return True

def validate_question(question: str) -> bool:
    """Validate feedback question"""
    if len(question.strip()) < 10:
        raise ValueError("Question too short (minimum 10 characters)")
    if len(question) > 500:
        raise ValueError("Question too long (maximum 500 characters)")
    return True

def validate_answer(answer: str) -> bool:
    """Validate feedback answer"""
    if len(answer.strip()) < 20:
        raise ValueError("Answer too short (minimum 20 characters)")
    if len(answer) > 2000:
        raise ValueError("Answer too long (maximum 2000 characters)")
    return True
