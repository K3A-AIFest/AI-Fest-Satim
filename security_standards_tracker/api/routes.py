"""
API endpoints for the security standards tracker.
"""
import logging
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Query, Depends

from security_standards_tracker.core.version_manager import StandardsVersionManager
from security_standards_tracker.config import STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH
from security_standards_tracker.models.data_models import StandardsList, VersionsList, StandardVersion, StandardChange
from retreiver import standards_retreiver

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Security Standards Tracker API", 
             description="API for tracking security standards updates and versions",
             version="1.0.0")

# Dependency for version manager
def get_version_manager() -> StandardsVersionManager:
    """Dependency for getting the version manager."""
    return StandardsVersionManager(STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH)

@app.get("/")
def root():
    """Root endpoint with API info."""
    return {
        "name": "Security Standards Tracker API",
        "version": "1.0.0",
        "description": "API for tracking security standards updates and versions"
    }

@app.get("/standards", response_model=StandardsList)
def list_standards(manager: StandardsVersionManager = Depends(get_version_manager)):
    """Get list of all standards."""
    return {"standards": manager.get_all_standards()}

@app.get("/standards/{standard_id}", response_model=StandardsList)
def get_standard(
    standard_id: str, 
    manager: StandardsVersionManager = Depends(get_version_manager)
):
    """Get information about a specific standard."""
    if standard_id not in manager.standards_index["standards"]:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    std_info = manager.standards_index["standards"][standard_id]
    return {"standards": [{**std_info, "id": standard_id}]}

@app.get("/standards/{standard_id}/versions", response_model=VersionsList)
def get_standard_versions(
    standard_id: str, 
    manager: StandardsVersionManager = Depends(get_version_manager)
):
    """Get all versions of a specific standard."""
    if standard_id not in manager.standards_index["standards"]:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    versions = manager.get_standard_versions(standard_id)
    return {"versions": versions}

@app.get("/versions/{version_id}", response_model=StandardVersion)
def get_version(
    version_id: str, 
    manager: StandardsVersionManager = Depends(get_version_manager)
):
    """Get a specific version of a standard."""
    version_data = manager.get_version(version_id)
    if not version_data:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return version_data

@app.get("/versions/{version_id}/changes", response_model=StandardChange)
def get_version_changes(
    version_id: str, 
    manager: StandardsVersionManager = Depends(get_version_manager)
):
    """Get changes between this version and the previous version."""
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
