from typing import List, Dict, Any
from tools.web import get_web_search_tools, web_search

def get_all_tools() -> List[Dict[str, Any]]:
    """
    Returns all available tools for agent binding.
    
    Returns:
        List of all tool definitions
    """
    tools = []
    
    # Add web search tools
    tools.extend(get_web_search_tools())
    
    # Add more tools here as they're developed
    
    return tools
