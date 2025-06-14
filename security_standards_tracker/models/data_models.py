"""
Models for data structures used in the standards tracker.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class StandardVersion(BaseModel):
    """Model representing a specific version of a security standard."""
    version_id: str
    standard_id: str
    standard_name: str
    version_date: str
    summary: str
    content: str
    source_url: Optional[str] = None


class StandardChange(BaseModel):
    """Model representing changes between two versions of a security standard."""
    change_id: str
    standard_id: str
    previous_version_id: Optional[str]
    new_version_id: str
    change_date: str
    summary: str
    changes: List[Dict[str, Any]]


class ChangeItem(BaseModel):
    """Model for individual change items between standard versions."""
    type: str = Field(..., description="Type of change: addition, removal, or modification")
    description: str = Field(..., description="Description of the change")
    content: str = Field(..., description="Content of the change")


class StandardsList(BaseModel):
    """Model for a list of standards."""
    standards: List[Dict[str, Any]]


class VersionsList(BaseModel):
    """Model for a list of standard versions."""
    versions: List[StandardVersion]


class SearchResult(BaseModel):
    """Model for search results."""
    standard_id: Optional[str] = None
    version_id: Optional[str] = None
    standard_name: Optional[str] = None
    version_date: Optional[str] = None
    content_preview: str
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
