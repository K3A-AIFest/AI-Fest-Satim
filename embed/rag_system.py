"""
RAG (Retrieval-Augmented Generation) system module.

This module provides the core RAG functionality for document indexing and retrieval.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import warnings
warnings.filterwarnings("ignore")

from llama_index.core import Settings, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.schema import Document, TextNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from embed.embeddings import EmbeddingManager
from embed.document_loader import DocumentLoader

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGSystem:
    """
    RAG System for document indexing and retrieval.
    
    Features:
    - Document chunking with customizable parameters
    - Vector storage and retrieval
    - Persistence (save/load)
    - Semantic search
    """
    
    def __init__(self, 
                 embedding_model: str = "BAAI/bge-m3",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize the RAG system.
        
        Args:
            embedding_model: HuggingFace model name for embeddings
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings
        self.embed_manager = EmbeddingManager(model_name=embedding_model)
        self.embed_model = self.embed_manager.get_embedding_model()
        
        # Set global settings for LlamaIndex
        Settings.embed_model = self.embed_model
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap
        
        logger.info(f"📝 Setting up text splitter (chunk_size={chunk_size}, overlap={chunk_overlap})")
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Document loader
        self.document_loader = DocumentLoader()
        
        # LlamaIndex components
        self.index = None
        self.documents = []
        self.is_trained = False
        
        logger.info(f"✅ RAG System initialized (using model: {embedding_model})")
    
    def load_documents(self, directory_path: str) -> List[Document]:
        """
        Load all supported files from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of LlamaIndex Document objects
        """
        documents = self.document_loader.load_from_directory(directory_path)
        self.documents = documents
        return documents
    
    def build_index(self, documents: List[Document] = None) -> bool:
        """
        Process documents and build the vector index.
        
        Args:
            documents: List of LlamaIndex Document objects (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if documents is None:
            documents = self.documents
            
        if not documents:
            logger.warning("⚠️  No documents to index!")
            return False
        
        try:
            logger.info(f"✂️  Processing {len(documents)} documents...")
            
            # Parse documents into nodes
            nodes = self.text_splitter.get_nodes_from_documents(documents)
            
            logger.info(f"📋 Created {len(nodes)} nodes/chunks")
            
            # Show chunking statistics
            if nodes:
                chunk_lengths = [len(node.text) for node in nodes]
                avg_length = sum(chunk_lengths) / len(chunk_lengths)
                logger.info(f"   Average chunk length: {avg_length:.0f} characters")
                logger.info(f"   Min chunk length: {min(chunk_lengths)}")
                logger.info(f"   Max chunk length: {max(chunk_lengths)}")
            
            # Build index
            logger.info("🔍 Creating Vector Index...")
            self.index = VectorStoreIndex(nodes)
            self.is_trained = True
            
            logger.info("✅ Index building completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error building index: {e}")
            return False
    
    def save_index(self, persist_dir: str) -> None:
        """
        Save index to disk.
        
        Args:
            persist_dir: Directory to save the index
        """
        if self.index is None:
            logger.error("❌ No index to save!")
            return
        
        try:
            # Create directory
            os.makedirs(persist_dir, exist_ok=True)
            
            # Save index
            self.index.storage_context.persist(persist_dir=persist_dir)
            
            # Save additional metadata
            metadata = {
                "embedding_model": self.embedding_model_name,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "document_count": len(self.documents),
            }
            
            with open(os.path.join(persist_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved index to: {persist_dir}")
            
        except Exception as e:
            logger.error(f"❌ Error saving index: {e}")
    
    def load_index(self, persist_dir: str) -> bool:
        """
        Load index from disk.
        
        Args:
            persist_dir: Directory containing the saved index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(persist_dir):
                logger.error(f"❌ Directory {persist_dir} does not exist!")
                return False
                
            # Load additional metadata if exists
            metadata_path = os.path.join(persist_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                self.embedding_model_name = metadata.get("embedding_model", self.embedding_model_name)
                self.chunk_size = metadata.get("chunk_size", self.chunk_size)
                self.chunk_overlap = metadata.get("chunk_overlap", self.chunk_overlap)
                
                # Update embed model if needed
                if hasattr(self.embed_model, 'model_name') and \
                   self.embedding_model_name != self.embed_model.model_name:
                    self.embed_manager = EmbeddingManager(model_name=self.embedding_model_name)
                    self.embed_model = self.embed_manager.get_embedding_model()
                    Settings.embed_model = self.embed_model

            # Create storage context
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            
            # Load index from storage
            self.index = load_index_from_storage(
                storage_context, 
                embed_model=self.embed_model
            )
            self.is_trained = True
            
            logger.info(f"📂 Loaded index from: {persist_dir}")
            logger.info(f"📊 Using embedding model: {self.embedding_model_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading index: {e}")
            return False
    
    def search(self, query: str, k: int = 5, similarity_threshold: float = 0.0) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: Search query string
            k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with metadata and scores
        """
        if self.index is None:
            logger.error("❌ No index loaded! Please create or load an index first.")
            return []
        
        logger.info(f"🔎 Searching for: '{query}'")
        
        try:
            # Create retriever
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=k,
            )
            
            # Execute query
            results = retriever.retrieve(query)
            
            # Prepare results
            formatted_results = []
            for i, node in enumerate(results):
                score = node.score if hasattr(node, 'score') else 0.0
                
                if score >= similarity_threshold:
                    result = {
                        'text': node.text,
                        'score': float(score) if score is not None else 0.0,
                        'rank': i + 1,
                        'node_id': node.node_id,
                    }
                    
                    # Add metadata
                    if hasattr(node, 'metadata') and node.metadata:
                        result.update(node.metadata)
                    
                    if 'filename' not in result and hasattr(node, 'metadata'):
                        result['filename'] = Path(node.metadata.get('file_path', 'unknown')).name
                        
                    formatted_results.append(result)
            
            logger.info(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error during search: {e}")
            return []
    
    def build_index_from_directory(self, directory_path: str) -> bool:
        """
        Complete pipeline: load documents and build index.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load documents
            documents = self.load_documents(directory_path)
            if not documents:
                logger.warning("⚠️  No documents found!")
                return False
            
            # Build index
            return self.build_index(documents)
            
        except Exception as e:
            logger.error(f"❌ Error building index from directory: {e}")
            return False
    
    def add_documents_to_existing_index(self, directory_path: str) -> bool:
        """
        Add new documents to an existing index.
        
        Args:
            directory_path: Path to directory containing new documents
            
        Returns:
            True if successful, False otherwise
        """
        if self.index is None:
            logger.error("❌ No existing index! Use build_index_from_directory instead.")
            return False
        
        try:
            # Load new documents
            new_documents = self.load_documents(directory_path)
            if not new_documents:
                logger.warning("⚠️  No new documents found!")
                return False
            
            logger.info(f"🔄 Adding {len(new_documents)} documents to existing index...")
            
            # Parse documents into nodes
            new_nodes = self.text_splitter.get_nodes_from_documents(new_documents)
            
            # Add to existing index
            self.index.insert_nodes(new_nodes)
            
            logger.info(f"✅ Added {len(new_nodes)} nodes to existing index")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error adding documents to index: {e}")
            return False
