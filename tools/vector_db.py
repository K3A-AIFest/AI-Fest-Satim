"""
Vector database retrieval tools for policies and standards.
"""
from typing import List, Dict, Any
from retreiver import polices_retreiver, standards_retreiver
from llama_index.core.schema import TextNode

def fetch_relevant_policies(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch relevant policy documents from the vector database.
    
    Args:
        query: The query to search for
        top_k: Maximum number of results to return
        
    Returns:
        List of relevant policy chunks with content and metadata
    """
    # Ensure top_k is within reasonable limits
    top_k = min(max(1, top_k), 20)
    
    # Retrieve relevant nodes
    retrieved_nodes = polices_retreiver.retrieve(query, similarity_top_k=top_k)
    
    # Process nodes into a standardized format
    results = []
    for node in retrieved_nodes:
        results.append({
            "content": node.text,
            "metadata": node.metadata,
            "score": node.score if hasattr(node, 'score') else None,
        })
    
    return results

def fetch_relevant_standards(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch relevant standards documents from the vector database.
    
    Args:
        query: The query to search for
        top_k: Maximum number of results to return
        
    Returns:
        List of relevant standard chunks with content and metadata
    """
    # Ensure top_k is within reasonable limits
    top_k = min(max(1, top_k), 20)
    
    # Retrieve relevant nodes
    retrieved_nodes = standards_retreiver.retrieve(query, similarity_top_k=top_k)
    
    # Process nodes into a standardized format
    results = []
    for node in retrieved_nodes:
        results.append({
            "content": node.text,
            "metadata": node.metadata,
            "score": node.score if hasattr(node, 'score') else None,
        })
    
    return results

def rewrite_query(query: str, context: str = None) -> str:
    """
    Rewrite a query to improve retrieval results.
    
    Args:
        query: The original query
        context: Additional context to guide query rewriting
        
    Returns:
        Rewritten query for better semantic search results
    """
    # This is a placeholder for a more sophisticated query rewriting approach
    # In a real-world implementation, this could use an LLM to rewrite the query
    
    # Simple rewrite logic - add key terms related to security policies and standards
    enhanced_query = query
    
    if "gap" in query.lower() or "missing" in query.lower():
        enhanced_query = f"identify gaps requirements {query}"
    elif "comply" in query.lower() or "compliance" in query.lower() or "conform" in query.lower():
        enhanced_query = f"compliance requirements regulations {query}"
    elif "enhance" in query.lower() or "improve" in query.lower() or "better" in query.lower():
        enhanced_query = f"improve enhance best practices {query}"
    
    return enhanced_query
