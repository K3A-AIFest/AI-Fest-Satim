"""
API server for the security standards tracker.

This module provides the main FastAPI application for the standards API.
"""
import logging
import os
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from security_standards_tracker.api.routes import app
from security_standards_tracker.utils.common import setup_logging, load_env

def main():
    """Start the API server."""
    # Load environment variables
    load_env()
    
    # Setup logging
    setup_logging("security_standards_api.log")
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Security Standards API server")
    
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", "8000"))
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
