"""
Embedding and RAG system module for information retrieval.

This module provides components for document processing, embedding generation,
and retrieval-augmented generation (RAG).
"""

from embed.embeddings import EmbeddingManager
from embed.document_loader import DocumentLoader
from embed.rag_system import RAGSystem
from embed.factory import RAGFactory

__all__ = [
    'EmbeddingManager',
    'DocumentLoader',
    'RAGSystem',
    'RAGFactory',
]