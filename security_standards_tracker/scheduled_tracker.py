#!/usr/bin/env python3
"""
Scheduled runner for the security standards tracker.

This script is designed to be run as a scheduled task (e.g., via cron)
to regularly fetch and update security standards.

Example crontab entry (runs daily at 3 AM):
0 3 * * * /path/to/python3 /path/to/scheduled_tracker.py >> /path/to/scheduled_tracker.log 2>&1
"""
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
os.chdir(project_root)  # Change to project root directory

from security_standards_tracker.utils.common import setup_logging, load_env
from security_standards_tracker.core.tracker import SecurityStandardsTracker

def main():
    """Main entry point for the scheduled tracker."""
    # Set up timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load environment variables
    load_env()
    
    # Set up logging with timestamped log file
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"scheduled_tracker_{timestamp}.log")
    
    setup_logging(log_file)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting scheduled security standards tracker run at {timestamp}")
    
    try:
        # Record start time
        start_time = time.time()
        
        # Run tracker
        tracker = SecurityStandardsTracker()
        tracker.run_fetch_cycle()
        
        # Calculate runtime
        runtime = time.time() - start_time
        logger.info(f"Scheduled run completed successfully in {runtime:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error in scheduled run: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
