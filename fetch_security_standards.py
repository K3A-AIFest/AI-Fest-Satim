#!/usr/bin/env python3
"""
Security Standards Tracker CLI

This script is a wrapper around the security_standards_tracker module's tracker_cli.py.
It provides a command-line interface for running the tracker.

Usage:
    python fetch_security_standards.py [--log-file LOG_FILE]
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

# Import the main module
from security_standards_tracker.tracker_cli import main

if __name__ == "__main__":
    main()
