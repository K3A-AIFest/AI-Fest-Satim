from typing import List, Dict, Any
from tools.web import web_search
from tools.vector_db import fetch_relevant_policies, fetch_relevant_standards, rewrite_query
from tools.kpi import get_kpi_tools


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
    
    # Add KPI tools
    tools.extend(get_kpi_tools())
    
    return tools

def get_base_tools() -> List[Dict[str, Any]]:
    """
    Returns the base tools without KPI functions.
    
    Returns:
        List of base tool definitions
    """
    return [
        fetch_relevant_policies,
        fetch_relevant_standards,
        rewrite_query,
        web_search
    ]

def get_kpi_only_tools() -> List[Dict[str, Any]]:
    """
    Returns only the KPI calculation tools.
    
    Returns:
        List of KPI tool definitions
    """
    return get_kpi_tools()

def get_tools_for_kpi_agent() -> List[Dict[str, Any]]:
    """
    Returns tools specifically for the KPI agent (base tools + KPI tools).
    
    Returns:
        List of tool definitions for KPI agent
    """
    tools = get_base_tools()
    tools.extend(get_kpi_tools())
    return tools
