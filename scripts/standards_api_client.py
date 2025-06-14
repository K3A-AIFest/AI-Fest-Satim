#!/usr/bin/env python3
"""
Example client for the Security Standards Tracker API.

This script demonstrates how to interact with the API endpoints.
"""
import requests
import json
import sys
import argparse
from typing import Dict, Any, List, Optional

# Default API URL (when running the API server locally)
DEFAULT_API_URL = "http://localhost:8000"

class SecurityStandardsClient:
    """Client for interacting with the Security Standards Tracker API."""
    
    def __init__(self, base_url: str = DEFAULT_API_URL):
        """Initialize the client with the API base URL."""
        self.base_url = base_url
    
    def list_standards(self) -> List[Dict[str, Any]]:
        """Get a list of all standards."""
        response = requests.get(f"{self.base_url}/standards")
        response.raise_for_status()
        return response.json()["standards"]
    
    def get_standard(self, standard_id: str) -> Dict[str, Any]:
        """Get information about a specific standard."""
        response = requests.get(f"{self.base_url}/standards/{standard_id}")
        response.raise_for_status()
        return response.json()["standards"][0]
    
    def get_standard_versions(self, standard_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a specific standard."""
        response = requests.get(f"{self.base_url}/standards/{standard_id}/versions")
        response.raise_for_status()
        return response.json()["versions"]
    
    def get_version(self, version_id: str) -> Dict[str, Any]:
        """Get a specific version of a standard."""
        response = requests.get(f"{self.base_url}/versions/{version_id}")
        response.raise_for_status()
        return response.json()
    
    def get_version_changes(self, version_id: str) -> Dict[str, Any]:
        """Get changes between this version and the previous version."""
        response = requests.get(f"{self.base_url}/versions/{version_id}/changes")
        response.raise_for_status()
        return response.json()
    
    def search_standards(self, query: str) -> List[Dict[str, Any]]:
        """Search for standards by keyword."""
        response = requests.get(f"{self.base_url}/search", params={"query": query})
        response.raise_for_status()
        return response.json()["results"]
    

def print_json(data: Any):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def main():
    """Main entry point for the client example."""
    parser = argparse.ArgumentParser(description="Security Standards Tracker API Client")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="API base URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List standards command
    subparsers.add_parser("list", help="List all standards")
    
    # Get standard command
    get_parser = subparsers.add_parser("get", help="Get a specific standard")
    get_parser.add_argument("standard_id", help="ID of the standard to get")
    
    # Get versions command
    versions_parser = subparsers.add_parser("versions", help="Get versions of a standard")
    versions_parser.add_argument("standard_id", help="ID of the standard")
    
    # Get specific version command
    version_parser = subparsers.add_parser("version", help="Get a specific version")
    version_parser.add_argument("version_id", help="ID of the version")
    
    # Get version changes command
    changes_parser = subparsers.add_parser("changes", help="Get changes for a version")
    changes_parser.add_argument("version_id", help="ID of the version")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for standards")
    search_parser.add_argument("query", help="Search query")
    
    args = parser.parse_args()
    
    # Initialize client
    client = SecurityStandardsClient(args.url)
    
    try:
        # Execute command
        if args.command == "list":
            standards = client.list_standards()
            print_json(standards)
            
        elif args.command == "get":
            standard = client.get_standard(args.standard_id)
            print_json(standard)
            
        elif args.command == "versions":
            versions = client.get_standard_versions(args.standard_id)
            print_json(versions)
            
        elif args.command == "version":
            version = client.get_version(args.version_id)
            print_json(version)
            
        elif args.command == "changes":
            changes = client.get_version_changes(args.version_id)
            print_json(changes)
            
        elif args.command == "search":
            results = client.search_standards(args.query)
            print_json(results)
            
        else:
            parser.print_help()
            
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
