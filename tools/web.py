from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def web_search(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web for the given query.
    
    Args:
        query: The search query
        max_results: Maximum number of search results to return
        
    Returns:
        List of search results with title, content, and URL
    """
    tavily_api_key = os.getenv("TAVI_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVI_API_KEY environment variable not set")
    
    search_tool = TavilySearchResults(
        tavily_api_key=tavily_api_key,
        max_results=max_results,
        k=max_results
    )
    
    return search_tool.invoke(query)
