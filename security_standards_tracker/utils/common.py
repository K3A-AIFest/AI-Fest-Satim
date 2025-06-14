"""
Utility functions for the security standards tracker.
"""
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
def setup_logging(log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        log_file: Optional file path to save logs
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=handlers
    )

def ensure_dir(path: str):
    """
    Ensure a directory exists.
    
    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    
def load_env():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logging.warning("python-dotenv not installed, skipping .env loading")
