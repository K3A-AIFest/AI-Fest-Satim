from typing import List, Dict, Any
from tools.web import web_search
from tools.vector_db import fetch_relevant_policies, fetch_relevant_standards, rewrite_query


def get_all_tools() -> List[Dict[str, Any]]:
    """
    Returns all available tools for agent binding.
    
    Returns:
        List of all tool definitions
    """
    tools = [
        
        fetch_relevant_policies,
        fetch_relevant_standards,
        rewrite_query,
        web_search
    ]
    

    # Add more tools here as they're developed
    
    return tools
