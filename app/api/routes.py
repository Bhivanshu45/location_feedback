from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas import (
    FeedbackSubmitRequest,
    FeedbackSubmitResponse,
    LocationAnalysisResponse,
    LocationInput,
    Concern
)
from app.database.connection import get_db
from app.database.models import Feedback
from app.rag.embeddings import get_embedding_generator
from app.rag.pipeline import RAGPipeline
from app.utils.logger import get_logger
from app.utils.validators import (
    validate_timestamp,
    validate_coordinates,
    validate_rating,
    validate_question,
    validate_answer
)
from datetime import datetime
import uuid

logger = get_logger(__name__)
router = APIRouter()

@router.post(
    "/feedback/submit",
    response_model=FeedbackSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Feedback"],
    summary="Submit multiple location feedbacks"
)
async def submit_feedback(
    request: FeedbackSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit multiple Q&A feedbacks for a location
    
    - **location**: GPS coordinates for the location
    - **timestamp**: When the feedback was provided
    - **feedbacks**: Array of 1-10 Q&A pairs with ratings
    - **user_id**: Optional user identifier
    
    Example:
    ```json
    {
      "location": {"lat": 28.6139, "long": 77.2090, "name": "Delhi"},
      "timestamp": "2026-02-19T10:30:00Z",
      "user_id": "user_001",
      "feedbacks": [
        {"question": "How safe?", "answer": "Very safe", "rating": 5},
        {"question": "Crowded?", "answer": "Yes", "rating": 4}
      ]
    }
    ```
    """
    try:
        # Validate location and timestamp
        validate_coordinates(request.location.lat, request.location.long)
        validate_timestamp(request.timestamp)
        
        feedback_ids = []
        
        # Process each Q&A pair
        embedding_gen = get_embedding_generator()
        for feedback_item in request.feedbacks:
            # Validate individual feedback
            validate_question(feedback_item.question)
            validate_answer(feedback_item.answer)
            validate_rating(feedback_item.rating)
            
            # Generate embedding for the answer
            embedding = embedding_gen.generate(feedback_item.answer)
            
            # Create feedback record
            feedback_id = uuid.uuid4()
            feedback = Feedback(
                id=feedback_id,
                user_id=request.user_id or "anonymous",
                question=feedback_item.question.strip(),
                answer=feedback_item.answer.strip(),
                location_lat=request.location.lat,
                location_long=request.location.long,
                location_name=request.location.name or "Unknown",
                rating=feedback_item.rating,
                timestamp=request.timestamp,
                embedding=embedding
            )
            
            db.add(feedback)
            feedback_ids.append(str(feedback_id))
        
        db.commit()
        
        logger.info(f"✅ Submitted {len(feedback_ids)} feedbacks for location {request.location.name}")
        
        return FeedbackSubmitResponse(
            success=True,
            feedback_ids=feedback_ids,
            count=len(feedback_ids),
            message=f"Successfully submitted {len(feedback_ids)} feedbacks",
            processing_status="completed"
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"❌ Error submitting feedback: {e}")
        logger.error(f"Full Traceback:\n{error_traceback}")
        print(f"\n{'='*80}")
        print(f"DETAILED ERROR TRACEBACK:")
        print(error_traceback)
        print(f"{'='*80}\n")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.get(
    "/location/analyze",
    response_model=LocationAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze location safety"
)
async def analyze_location(
    lat: float,
    long: float,
    name: str = "Unknown Location",
    db: Session = Depends(get_db)
):
    """
    Analyze location safety using RAG pipeline
    
    - **lat**: Latitude (-90 to 90)
    - **long**: Longitude (-180 to 180)
    - **name**: Location name (optional)
    
    Returns detailed safety analysis with:
    - Safety score (0-10)
    - Trend analysis (improving/stable/declining)
    - Time-based patterns
    - Community feedback synthesis
    - Actionable recommendations
    """
    try:
        # Validate coordinates
        validate_coordinates(lat, long)
        
        # Initialize RAG pipeline
        pipeline = RAGPipeline(db)
        
        # Run analysis
        analysis = pipeline.analyze_location(name, lat, long)
        
        logger.info(f"✅ Location analyzed: {name}")
        
        # Calculate status and color
        safety_score = float(analysis["safety_profile"]["score"])
        unsafe_probability = (10 - safety_score) / 10  # Convert to 0-1 scale
        
        if safety_score == 0:
            status = "No data available"
            color = "gray"
        elif safety_score >= 7:
            status = "Safe"
            color = "green"
        elif safety_score >= 5:
            status = "Moderate"
            color = "yellow"
        elif safety_score >= 3:
            status = "Caution"
            color = "orange"
        else:
            status = "Not Safe"
            color = "red"
        
        # Format concerns with severity
        concerns = []
        for concern in analysis["insights"]["top_concerns"]:
            concerns.append(Concern(
                title=concern,
                severity="medium"  # Could be enhanced with LLM analysis
            ))
        
        # Create summary
        reports_count = analysis["data_quality"]["reports_count"]
        if reports_count == 0:
            summary = f"No feedback available for {name} yet. Be the first to share your experience!"
        else:
            summary = f"{name} has {reports_count} feedback reports. Overall safety trend is {analysis['safety_profile']['trend']}. Review concerns and recommendations below."
        
        # Format response
        return LocationAnalysisResponse(
            location=LocationInput(lat=lat, long=long, name=name),
            unsafe_probability=unsafe_probability,
            status=status,
            color=color,
            trend=analysis["safety_profile"]["trend"],
            top_concerns=concerns[:5],
            recommendations=analysis["insights"]["recommendations"][:5],
            reports_count=reports_count,
            summary=summary
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error analyzing location: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze location"
        )

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app": "Location Safety RAG"
    }

@router.get("/", tags=["Info"])
async def root():
    """Root endpoint"""
    return {
        "message": "Location Safety RAG API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }
