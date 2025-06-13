"""
Helper utilities for RAG systems.
"""
import os
import logging
from typing import Dict, Any, Optional

from embed.rag_system import RAGSystem

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGFactory:
    """
    Factory class to create and manage RAG system instances.
    """
    
    @staticmethod
    def create_rag_system(
        embedding_model: str = "BAAI/bge-m3",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> RAGSystem:
        """
        Create a new RAG system instance with specified parameters.
        
        Args:
            embedding_model: Name of the embedding model to use
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            A configured RAG system instance
        """
        return RAGSystem(
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    @staticmethod
    def load_or_create_rag_system(
        persist_dir: str,
        documents_dir: str,
        embedding_model: str = "BAAI/bge-m3",
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> RAGSystem:
        """
        Load an existing RAG system from disk or create a new one if not found.
        
        Args:
            persist_dir: Directory where the index is/will be stored
            documents_dir: Directory containing documents to index
            embedding_model: Name of the embedding model to use
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            A configured RAG system instance with index loaded or created
        """
        # Initialize RAG system
        rag = RAGFactory.create_rag_system(
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Try to load existing index
        if os.path.exists(persist_dir) and rag.load_index(persist_dir):
            logger.info(f"✅ Loaded existing index from {persist_dir}")
            return rag
        else:
            # Create new index if loading failed
            logger.info(f"🔨 Building new index from {documents_dir}")
            if os.path.exists(documents_dir):
                if rag.build_index_from_directory(documents_dir):
                    # Save the newly created index
                    rag.save_index(persist_dir)
                    logger.info(f"💾 Saved new index to {persist_dir}")
                else:
                    logger.error(f"❌ Failed to build index from {documents_dir}")
            else:
                logger.error(f"❌ Documents directory {documents_dir} not found")
                
            return rag
