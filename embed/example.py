"""
Example script demonstrating how to use the refactored RAG system.
"""
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our RAG components
from embed import RAGFactory

def main():
    """
    Example of using the refactored RAG system for policies and standards.
    """
    # Paths for documents and index storage
    policies_dir = "policies"
    standards_dir = "standards"
    policies_persist_dir = "db/llamaindex_store_policies"
    standards_persist_dir = "db/llamaindex_store_standards"
    
    # Make sure db directory exists
    os.makedirs("db", exist_ok=True)
    
    # Create or load RAG systems
    logger.info("Initializing RAG systems...")
    
    # Policies RAG
    rag_policies = RAGFactory.load_or_create_rag_system(
        persist_dir=policies_persist_dir,
        documents_dir=policies_dir,
        embedding_model="BAAI/bge-m3",
        chunk_size=500,
        chunk_overlap=100
    )
    
    # Standards RAG
    rag_standards = RAGFactory.load_or_create_rag_system(
        persist_dir=standards_persist_dir,
        documents_dir=standards_dir,
        embedding_model="BAAI/bge-m3",
        chunk_size=500,
        chunk_overlap=100
    )
    
    # Example search query for each system
    logger.info("Searching in policies...")
    policies_results = rag_policies.search("access control requirements", k=3)
    
    logger.info("Searching in standards...")
    standards_results = rag_standards.search("NIST cybersecurity framework", k=3)
    
    # Return results (in a real application, you would process these results)
    return {
        "policies_results": policies_results,
        "standards_results": standards_results
    }

if __name__ == "__main__":
    main()
