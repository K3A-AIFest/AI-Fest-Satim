"""
Version manager for security standards.

This module handles the versioning of security standards, including:
- Adding new versions
- Tracking changes between versions
- Retrieving version history
"""
import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class StandardsVersionManager:
    """Manages different versions of security standards with versioning."""

    def __init__(self, versions_path: str, changes_path: str, embed_model=None, 
                 similarity_threshold: float = 0.75):
        """Initialize the version manager.
        
        Args:
            versions_path: Directory to store standard versions
            changes_path: Directory to store changes between versions
            embed_model: Model for calculating content similarities
            similarity_threshold: Threshold for considering content similar
        """
        self.versions_path = Path(versions_path)
        self.changes_path = Path(changes_path)
        self.embed_model = embed_model
        self.similarity_threshold = similarity_threshold
        
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
    
    def find_similar_standard(self, name: str, content: str, threshold: float = None) -> Optional[Dict[str, Any]]:
        """Find a similar standard based on name similarity and content similarity."""
        if threshold is None:
            threshold = self.similarity_threshold
            
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
            if self.embed_model is None:
                # Fallback to simple text similarity if no embed model
                return self._simple_text_similarity(content1, content2)
                
            # Use the embedding model
            embedding1 = self.embed_model.get_text_embedding(content1)
            embedding2 = self.embed_model.get_text_embedding(content2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            # Fallback to simple text similarity
            return self._simple_text_similarity(content1, content2)
            
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate a simple text similarity when embedding model fails."""
        # Normalize and split into words
        words1 = set(re.sub(r'[^\w\s]', '', text1.lower()).split())
        words2 = set(re.sub(r'[^\w\s]', '', text2.lower()).split())
        
        if not words1 or not words2:
            return 0.0
            
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
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
                
                if content_similarity > self.similarity_threshold:
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
