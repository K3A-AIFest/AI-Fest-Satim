"""
Embeddings module for vector embeddings using HuggingFace models.
"""
import logging
from typing import List, Dict, Any

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Manages embedding models for text embedding generation.
    
    This class provides a wrapper around HuggingFace embedding models
    to generate embeddings for text data in the RAG pipeline.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model_name = model_name
        logger.info(f"🤖 Loading embedding model: {model_name}")
        
        try:
            self.embed_model = HuggingFaceEmbedding(model_name=model_name)
            logger.info(f"✅ Embedding model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def get_embedding_model(self) -> Any:
        """
        Get the underlying embedding model.
        
        Returns:
            The HuggingFace embedding model instance
        """
        return self.embed_model
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text strings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (as lists of floats)
        """
        try:
            embeddings = [self.embed_model.get_text_embedding(text) for text in texts]
            return embeddings
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise
