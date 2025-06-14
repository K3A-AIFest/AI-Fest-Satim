"""
Security Standards News Tracker.

This script:
1. Fetches security standards news from the web
2. Processes and compares them with existing standards
3. Adds new information to the vector database with versioning
4. Provides an endpoint to retrieve different versions of standards

Usage:
    python security_standards_tracker.py --mode fetch  # Fetch and update standards
    python security_standards_tracker.py --mode serve  # Run the API endpoint server
"""
import argparse
import json
import logging
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from uvicorn import run as run_server

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
os.chdir(project_root)  # Change to project root directory

from tools.web import web_search
from embed.document_loader import DocumentLoader
from embed.factory import RAGFactory
from embed.rag_system import RAGSystem
from retreiver import embed_model, standards_retreiver, standards_index

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("security_standards_tracker.log"),
    ],
)
logger = logging.getLogger(__name__)

# Constants
STANDARDS_PATH = str(Path(project_root) / "db" / "llamaindex_store_standards")
STANDARDS_VERSIONS_PATH = str(Path(project_root) / "db" / "standards_versions")
STANDARDS_CHANGES_PATH = str(Path(project_root) / "db" / "standards_changes")
SEARCH_INTERVALS = 24 * 60 * 60  # 24 hours in seconds
SIMILARITY_THRESHOLD = 0.75  # Threshold for considering content similar

# Create necessary directories
os.makedirs(STANDARDS_VERSIONS_PATH, exist_ok=True)
os.makedirs(STANDARDS_CHANGES_PATH, exist_ok=True)

# Models for API
class StandardVersion(BaseModel):
    version_id: str
    standard_id: str
    standard_name: str
    version_date: str
    summary: str
    content: str
    source_url: Optional[str] = None

class StandardChange(BaseModel):
    change_id: str
    standard_id: str
    previous_version_id: Optional[str]
    new_version_id: str
    change_date: str
    summary: str
    changes: List[Dict[str, Any]]

class StandardsList(BaseModel):
    standards: List[Dict[str, Any]]

class VersionsList(BaseModel):
    versions: List[StandardVersion]

# Helper classes
class StandardsVersionManager:
    """Manages different versions of security standards with versioning."""

    def __init__(self, versions_path: str, changes_path: str):
        """Initialize the version manager.
        
        Args:
            versions_path: Directory to store standard versions
            changes_path: Directory to store changes between versions
        """
        self.versions_path = Path(versions_path)
        self.changes_path = Path(changes_path)
        
        # Ensure directories exist
        self.versions_path.mkdir(parents=True, exist_ok=True)
        self.changes_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing standards metadata
        self.standards_index_path = self.versions_path / "standards_index.json"
        self.standards_index = self._load_standards_index()
        
    def _load_standards_index(self) -> Dict[str, Any]:
        """Load the standards index file or create a new one if it doesn't exist."""
        if self.standards_index_path.exists():
            try:
                with open(self.standards_index_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Error loading standards index. Creating a new one.")
                return {"standards": {}}
        return {"standards": {}}
    
    def _save_standards_index(self):
        """Save the standards index to disk."""
        with open(self.standards_index_path, "w", encoding="utf-8") as f:
            json.dump(self.standards_index, f, indent=2)
    
    def get_standard_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get standard information by name."""
        for std_id, std_info in self.standards_index["standards"].items():
            if std_info["name"].lower() == name.lower():
                return {**std_info, "id": std_id}
        return None
    
    def find_similar_standard(self, name: str, content: str, threshold: float = 0.7) -> Optional[Dict[str, Any]]:
        """Find a similar standard based on name similarity and content similarity."""
        for std_id, std_info in self.standards_index["standards"].items():
            # Simple name similarity check
            if self._calculate_name_similarity(name, std_info["name"]) > threshold:
                # Get latest version of the standard
                latest_version = self.get_latest_version(std_id)
                if latest_version:
                    # Check content similarity
                    if self._calculate_content_similarity(content, latest_version["content"]) > threshold:
                        return {**std_info, "id": std_id}
        return None
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two standard names (simple implementation)."""
        # Normalize names
        name1 = re.sub(r'[^\w\s]', '', name1.lower())
        name2 = re.sub(r'[^\w\s]', '', name2.lower())
        
        # Split into words and find common words
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two standard contents using embeddings."""
        # Simple implementation using embeddings
        try:
            # Use the embedding model from retreiver.py
            embedding1 = embed_model.get_text_embedding(content1)
            embedding2 = embed_model.get_text_embedding(content2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    def add_standard(self, name: str, content: str, source_url: Optional[str] = None) -> Tuple[str, str, bool]:
        """
        Add a new standard or a new version of an existing standard.
        
        Returns:
            Tuple of (standard_id, version_id, is_new_standard)
        """
        # Check if similar standard exists
        similar_standard = self.find_similar_standard(name, content)
        
        if similar_standard:
            # This is likely a new version of an existing standard
            standard_id = similar_standard["id"]
            is_new_standard = False
            
            # Get the latest version
            latest_version = self.get_latest_version(standard_id)
            
            # Compare content to determine if this is truly a new version
            if latest_version:
                content_similarity = self._calculate_content_similarity(
                    content, latest_version["content"]
                )
                
                if content_similarity > SIMILARITY_THRESHOLD:
                    # Very similar to existing version, don't create new version
                    logger.info(f"Content is very similar to existing version (similarity: {content_similarity:.2f})")
                    return standard_id, latest_version["version_id"], False
            
            # Create new version for existing standard
            version_id = self._add_standard_version(
                standard_id, content, source_url
            )
            
            if latest_version:
                # Record the changes between versions
                self._add_standard_change(
                    standard_id, latest_version["version_id"], version_id,
                    self._generate_changes_summary(latest_version["content"], content)
                )
            
            logger.info(f"Added new version {version_id} for standard {standard_id}")
            
        else:
            # This is a completely new standard
            standard_id = f"std_{uuid.uuid4().hex[:10]}"
            is_new_standard = True
            
            # Create entry in standards index
            self.standards_index["standards"][standard_id] = {
                "name": name,
                "created_date": datetime.now().isoformat(),
                "versions": [],
                "latest_version": None,
            }
            
            # Add initial version
            version_id = self._add_standard_version(
                standard_id, content, source_url
            )
            
            logger.info(f"Added new standard {standard_id} with initial version {version_id}")
        
        # Save index changes
        self._save_standards_index()
        
        return standard_id, version_id, is_new_standard
    
    def _generate_changes_summary(self, old_content: str, new_content: str) -> List[Dict[str, Any]]:
        """Generate a summary of changes between two versions (simplified)."""
        # This is a simplified implementation - in production you might use
        # more sophisticated diff algorithms or even LLMs to summarize changes
        
        # Simple line-by-line diff
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        # Find added and removed lines (very basic approach)
        changes = []
        
        # Added lines (in new but not in old)
        added_lines = [line for line in new_lines if line.strip() and line not in old_lines]
        if added_lines:
            changes.append({
                "type": "addition",
                "description": f"Added {len(added_lines)} new lines",
                "content": "\n".join(added_lines[:5]) + ("..." if len(added_lines) > 5 else "")
            })
        
        # Removed lines (in old but not in new)
        removed_lines = [line for line in old_lines if line.strip() and line not in new_lines]
        if removed_lines:
            changes.append({
                "type": "removal",
                "description": f"Removed {len(removed_lines)} lines",
                "content": "\n".join(removed_lines[:5]) + ("..." if len(removed_lines) > 5 else "")
            })
            
        # If no specific changes detected
        if not changes:
            changes.append({
                "type": "modification",
                "description": "Content modified with no clear line additions/removals",
                "content": ""
            })
            
        return changes
    
    def _add_standard_version(self, standard_id: str, content: str, source_url: Optional[str] = None) -> str:
        """Add a new version of a standard."""
        version_id = f"v_{uuid.uuid4().hex[:10]}"
        version_date = datetime.now().isoformat()
        
        # Get standard info
        standard_info = self.standards_index["standards"][standard_id]
        standard_name = standard_info["name"]
        
        # Generate a summary (first 200 chars)
        summary = content[:200] + "..." if len(content) > 200 else content
        
        # Create version entry
        version_data = {
            "version_id": version_id,
            "standard_id": standard_id,
            "standard_name": standard_name,
            "version_date": version_date,
            "summary": summary,
            "content": content,
            "source_url": source_url
        }
        
        # Save version to disk
        version_file = self.versions_path / f"{version_id}.json"
        with open(version_file, "w", encoding="utf-8") as f:
            json.dump(version_data, f, indent=2)
        
        # Update standards index
        self.standards_index["standards"][standard_id]["versions"].append(version_id)
        self.standards_index["standards"][standard_id]["latest_version"] = version_id
        
        return version_id
    
    def _add_standard_change(self, standard_id: str, previous_version_id: str, 
                            new_version_id: str, changes: List[Dict[str, Any]]) -> str:
        """Record changes between two versions of a standard."""
        change_id = f"chg_{uuid.uuid4().hex[:10]}"
        change_date = datetime.now().isoformat()
        
        # Create change entry
        change_data = {
            "change_id": change_id,
            "standard_id": standard_id,
            "previous_version_id": previous_version_id,
            "new_version_id": new_version_id,
            "change_date": change_date,
            "summary": f"Changes from version {previous_version_id} to {new_version_id}",
            "changes": changes
        }
        
        # Save change to disk
        change_file = self.changes_path / f"{change_id}.json"
        with open(change_file, "w", encoding="utf-8") as f:
            json.dump(change_data, f, indent=2)
        
        return change_id
    
    def get_all_standards(self) -> List[Dict[str, Any]]:
        """Get list of all standards with basic info."""
        result = []
        for std_id, std_info in self.standards_index["standards"].items():
            latest_version_id = std_info.get("latest_version")
            latest_version = self.get_version(latest_version_id) if latest_version_id else None
            
            result.append({
                "id": std_id,
                "name": std_info["name"],
                "created_date": std_info["created_date"],
                "version_count": len(std_info["versions"]),
                "latest_version_id": latest_version_id,
                "latest_version_date": latest_version.get("version_date") if latest_version else None,
            })
        
        return result
    
    def get_standard_versions(self, standard_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a specific standard."""
        if standard_id not in self.standards_index["standards"]:
            return []
        
        versions = []
        for version_id in self.standards_index["standards"][standard_id]["versions"]:
            version_data = self.get_version(version_id)
            if version_data:
                versions.append(version_data)
        
        # Sort by date (newest first)
        versions.sort(key=lambda v: v["version_date"], reverse=True)
        return versions
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific version of a standard."""
        version_file = self.versions_path / f"{version_id}.json"
        if not version_file.exists():
            return None
        
        with open(version_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_latest_version(self, standard_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest version of a standard."""
        if standard_id not in self.standards_index["standards"]:
            return None
        
        latest_version_id = self.standards_index["standards"][standard_id].get("latest_version")
        if not latest_version_id:
            return None
        
        return self.get_version(latest_version_id)
    
    def get_version_changes(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get changes for a specific version (compared to previous)."""
        # Search through all changes to find the one with this new_version_id
        for change_file in self.changes_path.glob("*.json"):
            with open(change_file, "r", encoding="utf-8") as f:
                change_data = json.load(f)
                if change_data.get("new_version_id") == version_id:
                    return change_data
        return None


class SecurityStandardsTracker:
    """Main class for tracking security standards updates."""
    
    def __init__(self):
        """Initialize the tracker with version manager and RAG system."""
        self.version_manager = StandardsVersionManager(
            STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH
        )
        
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
        
        # List of security standards sources for targeted searches
        self.standard_sources = [
            "NIST Special Publications",
            "ISO 27001",
            "PCI DSS",
            "GDPR compliance",
            "SOC 2",
            "HIPAA",
            "CMMC cybersecurity",
            "CIS Controls",
            "OWASP Top 10",
        ]
    
    def fetch_security_standards_news(self):
        """Fetch security standards news from the web."""
        all_results = []
        
        # Search for updates to known standards
        for standard in self.standard_sources:
            search_query = f"{standard} new updates changes recent standards cybersecurity"
            logger.info(f"Searching for updates to {standard}...")
            
            try:
                results = web_search(search_query, max_results=5)
                if results:
                    all_results.extend(results)
            except Exception as e:
                logger.error(f"Error searching for {standard}: {e}")
        
        # Also search for general security standards updates
        general_queries = [
            "new cybersecurity standards updates",
            "recent changes security compliance requirements",
            "latest information security regulations updates",
            "cybersecurity framework updates recent",
        ]
        
        for query in general_queries:
            try:
                results = web_search(query, max_results=3)
                if results:
                    all_results.extend(results)
            except Exception as e:
                logger.error(f"Error with general search '{query}': {e}")
        
        logger.info(f"Found a total of {len(all_results)} search results")
        return all_results
    
    def _extract_standard_info(self, result):
        """Extract standard information from search result (simplified)."""
        # This is a simplified extraction - in production, you'd want more sophisticated
        # extraction, possibly with an LLM to help identify standard names, etc.
        
        # Try to determine standard name
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "")
        
        # Look for known standard patterns in title
        standard_name = None
        for source in self.standard_sources:
            if source in title or source in content[:200]:
                standard_name = source
                break
        
        # If no specific standard matched, use the title
        if not standard_name:
            # Try to clean up the title
            if ":" in title:
                # Take the part before the colon as the name
                standard_name = title.split(":")[0].strip()
            else:
                standard_name = title
        
        return {
            "name": standard_name,
            "content": content,
            "source_url": url
        }
    
    def process_search_results(self, results):
        """Process search results and add to version manager if they're new."""
        added_count = 0
        updated_count = 0
        
        for result in results:
            # Extract standard info from the result
            standard_info = self._extract_standard_info(result)
            
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
    
    def _add_to_vector_db(self, standard_id, version_id):
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
    
    def _update_in_vector_db(self, standard_id, version_id):
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
            # Fetch standards news
            results = self.fetch_security_standards_news()
            
            # Process results
            self.process_search_results(results)
            
            logger.info("Fetch cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in fetch cycle: {e}")


# API setup
app = FastAPI(title="Security Standards Tracker API")

@app.get("/")
def root():
    """Root endpoint with API info."""
    return {
        "name": "Security Standards Tracker API",
        "version": "1.0.0",
        "description": "API for tracking security standards updates and versions"
    }

@app.get("/standards", response_model=StandardsList)
def list_standards():
    """Get list of all standards."""
    manager = StandardsVersionManager(STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH)
    return {"standards": manager.get_all_standards()}

@app.get("/standards/{standard_id}", response_model=StandardsList)
def get_standard(standard_id: str):
    """Get information about a specific standard."""
    manager = StandardsVersionManager(STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH)
    
    if standard_id not in manager.standards_index["standards"]:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    std_info = manager.standards_index["standards"][standard_id]
    return {"standards": [{**std_info, "id": standard_id}]}

@app.get("/standards/{standard_id}/versions", response_model=VersionsList)
def get_standard_versions(standard_id: str):
    """Get all versions of a specific standard."""
    manager = StandardsVersionManager(STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH)
    
    if standard_id not in manager.standards_index["standards"]:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    versions = manager.get_standard_versions(standard_id)
    return {"versions": versions}

@app.get("/versions/{version_id}", response_model=StandardVersion)
def get_version(version_id: str):
    """Get a specific version of a standard."""
    manager = StandardsVersionManager(STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH)
    
    version_data = manager.get_version(version_id)
    if not version_data:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return version_data

@app.get("/versions/{version_id}/changes", response_model=StandardChange)
def get_version_changes(version_id: str):
    """Get changes between this version and the previous version."""
    manager = StandardsVersionManager(STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH)
    
    changes = manager.get_version_changes(version_id)
    if not changes:
        raise HTTPException(status_code=404, detail="Changes not found")
    
    return changes

@app.get("/search")
def search_standards(query: str = Query(..., min_length=3)):
    """Search for standards by keyword."""
    # Use the standards_retreiver from the retreiver module
    try:
        retrieved_nodes = standards_retreiver.retrieve(query)
        
        results = []
        for node in retrieved_nodes:
            # Check if this is from our versioned standards
            standard_id = node.metadata.get("standard_id")
            version_id = node.metadata.get("version_id")
            
            if standard_id and version_id:
                # This is one of our versioned standards
                results.append({
                    "standard_id": standard_id,
                    "version_id": version_id,
                    "standard_name": node.metadata.get("standard_name", "Unknown"),
                    "version_date": node.metadata.get("version_date", "Unknown"),
                    "content_preview": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                    "score": node.score if hasattr(node, "score") else None,
                })
            else:
                # This is from the original standards database
                results.append({
                    "content_preview": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                    "metadata": node.metadata,
                    "score": node.score if hasattr(node, "score") else None,
                })
        
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Error searching standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entrypoint for the script."""
    parser = argparse.ArgumentParser(description="Security Standards News Tracker")
    parser.add_argument("--mode", choices=["fetch", "serve"], default="fetch",
                      help="Mode to run: 'fetch' to update standards, 'serve' to run API")
    
    args = parser.parse_args()
    
    if args.mode == "fetch":
        # Run fetch cycle
        tracker = SecurityStandardsTracker()
        tracker.run_fetch_cycle()
    
    elif args.mode == "serve":
        # Run API server
        run_server(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
