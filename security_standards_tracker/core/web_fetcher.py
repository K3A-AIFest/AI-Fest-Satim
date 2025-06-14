"""
Web fetcher for security standards news.

This module handles fetching security standards updates from the web.
"""
import logging
from typing import Dict, List, Any, Optional

from tools.web import web_search
from security_standards_tracker.config import STANDARD_SOURCES, GENERAL_SEARCH_QUERIES, MAX_SEARCH_RESULTS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class SecurityNewsFetcher:
    """Fetches security standards news from the web."""
    
    def __init__(self, max_results: int = MAX_SEARCH_RESULTS):
        """
        Initialize the news fetcher.
        
        Args:
            max_results: Maximum number of search results per query
        """
        self.max_results = max_results
    
    def fetch_security_standards_news(self) -> List[Dict[str, Any]]:
        """
        Fetch security standards news from the web.
        
        Returns:
            List of search results with title, content, and URL
        """
        all_results = []
        
        # Search for updates to known standards
        for standard in STANDARD_SOURCES:
            search_query = f"{standard} new updates changes recent standards cybersecurity"
            logger.info(f"Searching for updates to {standard}...")
            
            try:
                results = web_search(search_query, max_results=self.max_results)
                if results:
                    all_results.extend(results)
            except Exception as e:
                logger.error(f"Error searching for {standard}: {e}")
        
        # Also search for general security standards updates
        for query in GENERAL_SEARCH_QUERIES:
            try:
                results = web_search(query, max_results=self.max_results)
                if results:
                    all_results.extend(results)
            except Exception as e:
                logger.error(f"Error with general search '{query}': {e}")
        
        logger.info(f"Found a total of {len(all_results)} search results")
        return all_results
    
    def extract_standard_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract standard information from search result.
        
        Args:
            result: Search result from web_search
            
        Returns:
            Dictionary with standard name, content, and source URL
        """
        # Try to determine standard name
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "")
        
        # Look for known standard patterns in title
        standard_name = None
        for source in STANDARD_SOURCES:
            if source in title or source in content[:200]:
                standard_name = source
                break
        
        # If no specific standard matched, use the title
        if not standard_name:
            # Try to clean up the title
            if ":" in title:
                # Take the part before the colon as the name
                standard_name = title.split(":")[0].strip()
            else:
                standard_name = title
        
        return {
            "name": standard_name,
            "content": content,
            "source_url": url
        }
