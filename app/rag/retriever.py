from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from app.database.models import Feedback
from app.config import get_settings
from app.rag.embeddings import get_embedding_generator
from app.utils.logger import get_logger
from typing import List
import numpy as np

logger = get_logger(__name__)
settings = get_settings()

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

class VectorRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_gen = get_embedding_generator()
    
    def retrieve_by_location(
        self, 
        lat: float, 
        long: float, 
        query_text: str,
        k: int = settings.RAG_K_RETRIEVAL,
        radius_km: float = settings.GEO_RADIUS_KM
    ) -> List[dict]:
        """
        Retrieve feedback using vector similarity + geo-proximity
        (Python-based, no pgvector needed)
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_gen.generate(query_text)
            
            # Get all feedback entries - don't filter by embedding on DB side
            # Let Python handle embedding filtering
            query_results = self.db.query(Feedback).all()
            
            # Calculate similarity scores in Python
            scored_results = []
            for feedback in query_results:
                # Skip if no embedding
                if not feedback.embedding:
                    continue
                    
                similarity = cosine_similarity(query_embedding, feedback.embedding)
                distance_km = (
                    np.sqrt(
                        (feedback.location_lat - lat)**2 + 
                        (feedback.location_long - long)**2
                    ) * 111
                )
                
                scored_results.append({
                    "feedback": feedback,
                    "similarity": similarity,
                    "distance_km": distance_km
                })
            
            # Sort by similarity (desc) then distance (asc)
            scored_results.sort(
                key=lambda x: (-x["similarity"], x["distance_km"])
            )
            
            # Take top K results - remove strict similarity threshold
            results = []
            for item in scored_results[:k]:
                feedback = item["feedback"]
                results.append({
                    "id": str(feedback.id),
                    "question": feedback.question,
                    "answer": feedback.answer,
                    "rating": feedback.rating,
                    "timestamp": feedback.timestamp.isoformat(),
                    "category": feedback.category or "general",
                    "sentiment": feedback.sentiment or "neutral",
                    "similarity": item["similarity"],
                    "distance_km": item["distance_km"]
                })
            
            logger.info(f"Retrieved {len(results)} feedback entries for location ({lat}, {long})")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving feedback: {e}")
            return []
