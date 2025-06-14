#!/usr/bin/env python3
"""
Scheduled runner for the Security Standards Tracker.

This script can be used to run the tracker on a regular schedule.
It can be triggered by a cron job or a similar scheduler.

Example crontab entry (runs daily at 3 AM):
0 3 * * * /usr/bin/python3 /path/to/scheduled_standards_tracker.py >> /path/to/tracker_log.log 2>&1
"""
import os
import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
os.chdir(project_root)  # Change to project root directory

from scripts.security_standards_tracker import SecurityStandardsTracker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scheduled_standards_tracker.log"),
    ],
)
logger = logging.getLogger(__name__)

def run_tracker_with_retries(max_retries=3, retry_delay=300):
    """
    Run the security standards tracker with retries in case of failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retry attempts (seconds)
    """
    attempts = 0
    
    while attempts < max_retries:
        try:
            logger.info(f"Running security standards tracker (attempt {attempts + 1}/{max_retries})")
            
            # Create and run the tracker
            tracker = SecurityStandardsTracker()
            tracker.run_fetch_cycle()
            
            logger.info("Security standards tracker completed successfully")
            return True
            
        except Exception as e:
            attempts += 1
            logger.error(f"Error running security standards tracker: {e}")
            
            if attempts < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Giving up.")
                return False

def main():
    """Main entry point for the scheduled runner."""
    parser = argparse.ArgumentParser(description="Scheduled Security Standards Tracker Runner")
    parser.add_argument("--notify", action="store_true", help="Enable notifications on completion")
    parser.add_argument("--output", type=str, help="Path to additional output log file")
    
    args = parser.parse_args()
    
    # Run the tracker
    start_time = datetime.now()
    logger.info(f"Starting scheduled run at {start_time}")
    
    success = run_tracker_with_retries()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"Run completed at {end_time} (duration: {duration})")
    logger.info(f"Status: {'Success' if success else 'Failed'}")
    
    # Log to additional output file if specified
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - Security Standards Tracker - {'Success' if success else 'Failed'}\n")
    
    # Send notification if requested and available
    if args.notify and success:
        try:
            # Simple command-line notification (Linux)
            if sys.platform.startswith('linux'):
                os.system('notify-send "Security Standards Tracker" "Update completed successfully"')
            # Could add more notification methods here
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

if __name__ == "__main__":
    main()
