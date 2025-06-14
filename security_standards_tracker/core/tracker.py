"""
Security Standards Tracker core functionality.

This module combines version management, web fetching, and vector DB integration.
"""
import logging
from typing import Dict, List, Any, Tuple, Optional

from llama_index.core.schema import Document

from security_standards_tracker.config import (
    STANDARDS_PATH, 
    STANDARDS_VERSIONS_PATH, 
    STANDARDS_CHANGES_PATH,
    SIMILARITY_THRESHOLD
)
from security_standards_tracker.core.version_manager import StandardsVersionManager
from security_standards_tracker.core.web_fetcher import SecurityNewsFetcher
from retreiver import embed_model
from embed.document_loader import DocumentLoader
from embed.factory import RAGFactory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class SecurityStandardsTracker:
    """Main class for tracking security standards updates."""
    
    def __init__(self):
        """Initialize the tracker with version manager and RAG system."""
        self.version_manager = StandardsVersionManager(
            STANDARDS_VERSIONS_PATH, 
            STANDARDS_CHANGES_PATH,
            embed_model,
            SIMILARITY_THRESHOLD
        )
        
        # Web fetcher for retrieving news
        self.web_fetcher = SecurityNewsFetcher()
        
        # Load existing RAG system
        self.rag_factory = RAGFactory()
        self.rag_system = self.rag_factory.load_or_create_rag_system(
            persist_dir=STANDARDS_PATH,
            documents_dir="./standards",
            embedding_model="BAAI/bge-m3",
            chunk_size=500,
            chunk_overlap=100
        )
        
        self.document_loader = DocumentLoader()
    
    def fetch_and_process_standards(self) -> Tuple[int, int]:
        """
        Fetch standards news and process the results.
        
        Returns:
            Tuple of (added_count, updated_count)
        """
        # Fetch news
        results = self.web_fetcher.fetch_security_standards_news()
        
        # Process results
        return self.process_search_results(results)
    
    def process_search_results(self, results: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Process search results and add to version manager if they're new.
        
        Args:
            results: List of search results
            
        Returns:
            Tuple of (added_count, updated_count)
        """
        added_count = 0
        updated_count = 0
        
        for result in results:
            # Extract standard info from the result
            standard_info = self.web_fetcher.extract_standard_info(result)
            
            # Skip if content is too short
            if len(standard_info["content"]) < 100:
                continue
            
            # Add to version manager (handles versioning internally)
            try:
                standard_id, version_id, is_new_standard = self.version_manager.add_standard(
                    standard_info["name"],
                    standard_info["content"],
                    standard_info["source_url"]
                )
                
                if is_new_standard:
                    added_count += 1
                    # Add to vector DB as a new document
                    self._add_to_vector_db(standard_id, version_id)
                else:
                    updated_count += 1
                    # Update existing document in vector DB
                    self._update_in_vector_db(standard_id, version_id)
                    
            except Exception as e:
                logger.error(f"Error processing standard {standard_info['name']}: {e}")
        
        logger.info(f"Processed {len(results)} results. Added {added_count} new standards and updated {updated_count} existing standards.")
        return added_count, updated_count
    
    def _add_to_vector_db(self, standard_id: str, version_id: str):
        """Add a new standard to the vector database."""
        try:
            # Get version data
            version_data = self.version_manager.get_version(version_id)
            if not version_data:
                logger.error(f"Version data not found for {version_id}")
                return
            
            # Create a document
            doc = Document(
                text=version_data["content"],
                metadata={
                    "standard_id": standard_id,
                    "version_id": version_id,
                    "standard_name": version_data["standard_name"],
                    "version_date": version_data["version_date"],
                    "source_url": version_data.get("source_url", "")
                }
            )
            
            # Add document to index
            self.rag_system.add_documents([doc])
            
            # Persist the index
            self.rag_system.persist()
            
            logger.info(f"Added new standard {standard_id}:{version_id} to vector DB")
            
        except Exception as e:
            logger.error(f"Error adding standard to vector DB: {e}")
    
    def _update_in_vector_db(self, standard_id: str, version_id: str):
        """Update an existing standard in the vector database."""
        try:
            # Get version data
            version_data = self.version_manager.get_version(version_id)
            if not version_data:
                logger.error(f"Version data not found for {version_id}")
                return
                
            # In this implementation, we'll add a new document with the updated content
            # For a production system, you might want to update the existing nodes
            
            # Create a document
            doc = Document(
                text=version_data["content"],
                metadata={
                    "standard_id": standard_id,
                    "version_id": version_id,
                    "standard_name": version_data["standard_name"],
                    "version_date": version_data["version_date"],
                    "source_url": version_data.get("source_url", ""),
                    "is_update": True,
                    "updates_standard_id": standard_id,
                }
            )
            
            # Add document to index
            self.rag_system.add_documents([doc])
            
            # Persist the index
            self.rag_system.persist()
            
            logger.info(f"Updated standard {standard_id} with new version {version_id} in vector DB")
            
        except Exception as e:
            logger.error(f"Error updating standard in vector DB: {e}")
    
    def run_fetch_cycle(self):
        """Run a complete fetch and update cycle."""
        logger.info("Starting standards update fetch cycle")
        
        try:
            # Fetch and process standards
            added, updated = self.fetch_and_process_standards()
            
            logger.info(f"Fetch cycle completed successfully. Added {added} new standards and updated {updated} existing standards.")
            
        except Exception as e:
            logger.error(f"Error in fetch cycle: {e}")
            
    def get_standards_manager(self) -> StandardsVersionManager:
        """Get the standards version manager instance."""
        return self.version_manager
