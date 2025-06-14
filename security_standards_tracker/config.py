"""
Configuration for the security standards tracker.
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
STANDARDS_PATH = os.path.join(BASE_DIR, "db/llamaindex_store_standards")
STANDARDS_VERSIONS_PATH = os.path.join(BASE_DIR, "db/standards_versions")
STANDARDS_CHANGES_PATH = os.path.join(BASE_DIR, "db/standards_changes")

# Search settings
SEARCH_INTERVALS = 24 * 60 * 60  # 24 hours in seconds
SIMILARITY_THRESHOLD = 0.75  # Threshold for considering content similar
MAX_SEARCH_RESULTS = 5  # Maximum number of search results per query

# Standard sources to track
STANDARD_SOURCES = [
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

# General search queries
GENERAL_SEARCH_QUERIES = [
    "new cybersecurity standards updates",
    "recent changes security compliance requirements",
    "latest information security regulations updates",
    "cybersecurity framework updates recent",
]

# Ensure directories exist
os.makedirs(STANDARDS_VERSIONS_PATH, exist_ok=True)
os.makedirs(STANDARDS_CHANGES_PATH, exist_ok=True)
