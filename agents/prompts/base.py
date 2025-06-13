WEB_SEARCH_PROMPT_SUFFIX = """
You have access to a web search tool that can help you find up-to-date information. 
When you need to search for information that might not be in your training data or requires current data:
1. Use the web search tool by calling the appropriate function
2. Analyze the search results carefully
3. Incorporate the factual information into your response
4. Cite sources when appropriate

Remember to use the web search tool when questions involve:
- Current events or recent developments
- Specific facts that need verification
- Topics that may have changed since your training data cutoff
- Requests for up-to-date information

Always use the web search tool responsibly and only when necessary.
"""

def get_web_enhanced_prompt(base_prompt: str) -> str:
    """
    Enhances a base system prompt with instructions for using web search.
    
    Args:
        base_prompt: The original system prompt
        
    Returns:
        Enhanced prompt that includes web search instructions
    """
    return f"{base_prompt}\n\n{WEB_SEARCH_PROMPT_SUFFIX}"
