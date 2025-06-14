"""
Main entry point for the security standards tracker.

This module provides a command-line interface for the security standards tracker.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
os.chdir(project_root)  # Change to project root directory

from security_standards_tracker.core.tracker import SecurityStandardsTracker
from security_standards_tracker.utils.common import setup_logging, load_env

def main():
    """Main entry point for the security standards tracker."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Security Standards News Tracker")
    parser.add_argument("--log-file", 
                      help="Log file path (default: security_standards_tracker.log)",
                      default="security_standards_tracker.log")
    args = parser.parse_args()
    
    # Load environment variables
    load_env()
    
    # Setup logging
    setup_logging(args.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Security Standards Tracker")
    
    try:
        # Initialize and run the tracker
        tracker = SecurityStandardsTracker()
        tracker.run_fetch_cycle()
        
        logger.info("Security Standards Tracker completed successfully")
        
    except Exception as e:
        logger.error(f"Error running Security Standards Tracker: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
