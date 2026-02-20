import json
from typing import Dict, Any
from app.config import get_settings
from app.utils.logger import get_logger
from groq import Groq

logger = get_logger(__name__)
settings = get_settings()

class RAGGenerator:
    def __init__(self):
        self.llm_type = settings.LLM_TYPE
        self.model = settings.LLM_MODEL
        
        if self.llm_type == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set in environment")
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info(f"Initialized Groq LLM with model: {self.model}")
        else:
            raise ValueError(f"Unknown LLM type: {self.llm_type}")
    
    def generate_analysis(
        self, 
        location_name: str,
        retrieved_feedback: list
    ) -> Dict[str, Any]:
        """
        Use Groq LLM to generate location analysis from retrieved feedback
        """
        if not retrieved_feedback:
            return self._get_no_data_response()
        
        # Format context from retrieved feedback
        context = self._format_context(retrieved_feedback)
        
        prompt = f"""You are a location safety analyst. Based on the following user feedback about {location_name}:

{context}

Generate a detailed JSON response with ONLY valid JSON (no markdown) with the following structure:
{{
    "safety_score": <number 1-10>,
    "trend": "<improving|stable|declining>",
    "confidence": <number 0-1>,
    "top_concerns": [<3 main safety concerns as strings>],
    "positive_aspects": [<3 positive things as strings>],
    "time_patterns": {{
        "morning": "<Safe|Moderate|Caution>",
        "afternoon": "<Safe|Moderate|Caution>",
        "evening": "<Safe|Moderate|Caution>",
        "night": "<Safe|Moderate|Caution>"
    }},
    "recommendations": [<3-5 safety recommendations as strings>]
}}

IMPORTANT: Return ONLY valid JSON, no markdown, no extra text, no code blocks."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean response if it has markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            logger.info(f"Generated analysis for {location_name}")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._get_default_response()
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return self._get_default_response()
    
    def _format_context(self, feedback: list) -> str:
        """Format retrieved feedback into readable context"""
        context = ""
        for i, item in enumerate(feedback, 1):
            context += f"""
Feedback #{i}:
Q: {item['question']}
A: {item['answer']}
Rating: {item['rating']}/5
Category: {item['category']}
Sentiment: {item['sentiment']}
---"""
        return context
    
    def _get_default_response(self) -> Dict[str, Any]:
        """Fallback response"""
        return {
            "safety_score": 5.0,
            "trend": "stable",
            "confidence": 0.5,
            "top_concerns": ["Insufficient data for detailed analysis"],
            "positive_aspects": ["Data collection in progress"],
            "time_patterns": {
                "morning": "Moderate",
                "afternoon": "Moderate",
                "evening": "Moderate",
                "night": "Moderate"
            },
            "recommendations": ["Provide more feedback for better analysis"]
        }
    
    def _get_no_data_response(self) -> Dict[str, Any]:
        """Response when no data available"""
        return {
            "safety_score": 0,
            "trend": "stable",
            "confidence": 0,
            "top_concerns": ["No data available"],
            "positive_aspects": [],
            "time_patterns": {
                "morning": "Unknown",
                "afternoon": "Unknown",
                "evening": "Unknown",
                "night": "Unknown"
            },
            "recommendations": ["Please provide feedback"]
        }
