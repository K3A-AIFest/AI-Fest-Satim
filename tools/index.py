from typing import List, Dict, Any
from tools.web import web_search
from tools.vector_db import fetch_relevant_policies, fetch_relevant_standards, rewrite_query

def get_web_search_tools() -> List[Dict[str, Any]]:
    """
    Returns web search tool definitions.
    
    Returns:
        Web search tool definition
    """
    return [{
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information on security standards, compliance requirements, or best practices",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return"
                    }
                },
                "required": ["query"]
            }
        }
    }]

def get_vector_db_tools() -> List[Dict[str, Any]]:
    """
    Returns vector database retrieval tool definitions.
    
    Returns:
        List of vector database tool definitions
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "fetch_relevant_policies",
                "description": "Search the policies vector database for relevant policy documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant policies"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of policy chunks to return (default: 10, max: 20)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_relevant_standards",
                "description": "Search the standards vector database for relevant standards documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant standards"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of standard chunks to return (default: 10, max: 20)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rewrite_query",
                "description": "Rewrite a query to improve vector database search results",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The original search query"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context to guide query rewriting"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

def get_all_tools() -> List[Dict[str, Any]]:
    """
    Returns all available tools for agent binding.
    
    Returns:
        List of all tool definitions
    """
    tools = []
    
    # Add web search tools
    tools.extend(get_web_search_tools())
    
    # Add vector database tools
    tools.extend(get_vector_db_tools())
    
    # Add more tools here as they're developed
    
    return tools
