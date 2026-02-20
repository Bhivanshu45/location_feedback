from sqlalchemy.orm import Session
from app.rag.embeddings import get_embedding_generator
from app.rag.retriever import VectorRetriever
from app.rag.generator import RAGGenerator
from app.database.models import Feedback
from app.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class RAGPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_gen = get_embedding_generator()
        self.retriever = VectorRetriever(db)
        self.generator = RAGGenerator()
    
    def process_feedback(self, feedback_id: str):
        """Process feedback: extract insights, generate embeddings"""
        try:
            feedback = self.db.query(Feedback).filter(
                Feedback.id == feedback_id
            ).first()
            
            if not feedback:
                logger.error(f"Feedback {feedback_id} not found")
                return
            
            # Generate embedding
            combined_text = f"{feedback.question} {feedback.answer}"
            embedding = self.embedding_gen.generate(combined_text)
            
            # Extract category & sentiment using LLM
            category = self._extract_category(feedback.question)
            sentiment = self._extract_sentiment(feedback.answer)
            
            # Update feedback
            feedback.embedding = embedding
            feedback.category = category
            feedback.sentiment = sentiment
            self.db.commit()
            
            logger.info(f"Processed feedback {feedback_id}")
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            self.db.rollback()
    
    def analyze_location(
        self, 
        location_name: str,
        lat: float, 
        long: float
    ) -> dict:
        """Full RAG pipeline for location analysis"""
        
        # Retrieve relevant feedback
        query_text = f"Safety of {location_name}"
        retrieved = self.retriever.retrieve_by_location(
            lat, long, query_text
        )
        
        if not retrieved:
            return self._get_no_data_response(location_name, lat, long)
        
        # Generate analysis using LLM
        analysis = self.generator.generate_analysis(
            location_name, retrieved
        )
        
        # Calculate data freshness
        try:
            recent_date = max(
                [datetime.fromisoformat(f["timestamp"]) for f in retrieved]
            )
            freshness_hours = int((datetime.utcnow() - recent_date).total_seconds() / 3600)
        except:
            freshness_hours = 0
        
        return {
            "safety_profile": {
                "score": float(analysis.get("safety_score", 5.0)),
                "trend": analysis.get("trend", "stable"),
                "confidence": float(analysis.get("confidence", 0.5))
            },
            "insights": {
                "top_concerns": analysis.get("top_concerns", []),
                "positive_aspects": analysis.get("positive_aspects", []),
                "time_patterns": analysis.get("time_patterns", {}),
                "recommendations": analysis.get("recommendations", [])
            },
            "data_quality": {
                "reports_count": len(retrieved),
                "date_range": "Last 90 days",
                "last_updated": f"{freshness_hours} hours ago",
                "data_freshness_hours": freshness_hours
            }
        }
    
    def _extract_category(self, question: str) -> str:
        """Extract safety concern category using LLM"""
        try:
            response = self.generator.client.chat.completions.create(
                model=self.generator.model,
                messages=[{
                    "role": "user",
                    "content": f"Classify this safety question into ONE category: theft, violence, harassment, infrastructure, or other. Question: '{question}'. Reply with only the category."
                }],
                max_tokens=20,
                temperature=0.3
            )
            category = response.choices[0].message.content.strip().lower()
            valid_categories = ["theft", "violence", "harassment", "infrastructure", "other"]
            return category if category in valid_categories else "other"
        except Exception as e:
            logger.warning(f"Error extracting category: {e}")
            return "other"
    
    def _extract_sentiment(self, answer: str) -> str:
        """Extract sentiment using LLM"""
        try:
            response = self.generator.client.chat.completions.create(
                model=self.generator.model,
                messages=[{
                    "role": "user",
                    "content": f"Classify the sentiment as positive, neutral, or negative. Answer: '{answer}'. Reply with only the sentiment."
                }],
                max_tokens=20,
                temperature=0.3
            )
            sentiment = response.choices[0].message.content.strip().lower()
            valid_sentiments = ["positive", "neutral", "negative"]
            return sentiment if sentiment in valid_sentiments else "neutral"
        except Exception as e:
            logger.warning(f"Error extracting sentiment: {e}")
            return "neutral"


    
    def _get_no_data_response(self, location_name: str, lat: float, long: float) -> dict:
        """Return response when no feedback exists for location"""
        return {
            "safety_profile": {
                "score": 0,
                "trend": "stable",
                "confidence": 0
            },
            "insights": {
                "top_concerns": ["No data available for this location yet"],
                "positive_aspects": [],
                "time_patterns": {
                    "morning": "Unknown",
                    "afternoon": "Unknown",
                    "evening": "Unknown",
                    "night": "Unknown"
                },
                "recommendations": ["Be the first to provide feedback about this location"]
            },
            "data_quality": {
                "reports_count": 0,
                "date_range": "N/A",
                "last_updated": "Never",
                "data_freshness_hours": 0
            }
        }

        """Extract sentiment"""
        positive_words = ["safe", "good", "great", "excellent", "perfect", "best"]
        negative_words = ["unsafe", "bad", "dangerous", "poor", "terrible", "worst"]
        
        answer_lower = answer.lower()
        pos_count = sum(1 for word in positive_words if word in answer_lower)
        neg_count = sum(1 for word in negative_words if word in answer_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"
    
    def _get_no_data_response(self, location_name, lat, long):
        """Response when no data available"""
        return {
            "safety_profile": {
                "score": 0,
                "trend": "stable",
                "confidence": 0
            },
            "insights": {
                "top_concerns": ["No data available for this location"],
                "positive_aspects": [],
                "time_patterns": {
                    "morning": "Unknown",
                    "afternoon": "Unknown",
                    "evening": "Unknown",
                    "night": "Unknown"
                },
                "recommendations": ["Be the first to provide feedback!"]
            },
            "data_quality": {
                "reports_count": 0,
                "date_range": "N/A",
                "last_updated": "Never",
                "data_freshness_hours": 999999
            }
        }
