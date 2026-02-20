from sentence_transformers import SentenceTransformer
from app.config import get_settings
from app.utils.logger import get_logger
from typing import List
import numpy as np

logger = get_logger(__name__)
settings = get_settings()

class EmbeddingGenerator:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            raise

    def generate(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            if isinstance(text, str):
                embedding = self.model.encode(text, convert_to_tensor=False)
            else:
                embedding = self.model.encode(str(text), convert_to_tensor=False)
            
            # Convert numpy array to list
            return embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * settings.EMBEDDING_DIMENSION

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [e.tolist() if isinstance(e, np.ndarray) else e for e in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]


# Global instance
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create embedding generator instance"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
