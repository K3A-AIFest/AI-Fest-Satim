#!/usr/bin/env python3
"""
Security Standards API Server

This script is a wrapper around the security_standards_tracker module's api_server.py.
It starts the FastAPI server for the security standards API.

Usage:
    python start_standards_api.py
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

# Import the main module
from security_standards_tracker.api_server import main

if __name__ == "__main__":
    main()
