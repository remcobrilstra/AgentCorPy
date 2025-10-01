"""
Hybrid web search tool for the AgentCorp framework

Uses duckduckgo-search library as primary method with Brave Search API fallback
"""

import os
from typing import Dict, Any, List
import requests
import json

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext


def web_search(context: ToolExecutionContext, query: str, num_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo library with Brave Search API fallback.

    Args:
        context: Tool execution context
        query: The search query
        num_results: Number of results to return (default: 5, max: 10)

    Returns:
        str: Formatted search results
    """
    try:
        # Limit results to reasonable number
        num_results = min(max(1, num_results), 10)
        
        # Primary method: Use ddgs library (free)
        try:
            from ddgs import DDGS
            
            results = []
            with DDGS() as ddgs:
                # Get web search results
                search_results = ddgs.text(
                    query=query,
                    max_results=num_results,
                    safesearch='moderate'
                )
                
                for result in search_results:
                    results.append({
                        "title": result.get('title', 'No title'),
                        "url": result.get('href', ''),
                        "snippet": result.get('body', 'No description available')
                    })
            
            if results:
                return _format_search_results(query, results, "DuckDuckGo")
                
        except Exception as ddg_error:
            print(f"DuckDuckGo search failed: {ddg_error}")
            
            # Fallback: Try Brave Search API if API key is available
            brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY')
            if brave_api_key:
                try:
                    return _brave_search_fallback(query, num_results, brave_api_key)
                except Exception as brave_error:
                    print(f"Brave Search fallback failed: {brave_error}")
            
            # If both fail, return error with helpful message
            return (f"Search failed for query: '{query}'\n\n"
                   f"Primary (DuckDuckGo): {str(ddg_error)}\n"
                   f"Fallback (Brave): {'API key not found' if not brave_api_key else 'API call failed'}\n\n"
                   f"To enable Brave Search fallback, set BRAVE_SEARCH_API_KEY environment variable.\n"
                   f"Get a free API key at: https://api-dashboard.search.brave.com/")

    except Exception as e:
        return f"Error performing web search for '{query}': {str(e)}"


def _brave_search_fallback(query: str, num_results: int, api_key: str) -> str:
    """
    Fallback search using Brave Search API
    
    Args:
        query: Search query
        num_results: Number of results to return
        api_key: Brave Search API key
    
    Returns:
        str: Formatted search results
    """
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": num_results,
        "safesearch": "moderate",
        "search_lang": "en",
        "ui_lang": "en-US"
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    # Extract web results
    web_results = data.get('web', {}).get('results', [])
    for result in web_results[:num_results]:
        results.append({
            "title": result.get('title', 'No title'),
            "url": result.get('url', ''),
            "snippet": result.get('description', 'No description available')
        })
    
    return _format_search_results(query, results, "Brave Search")


def _format_search_results(query: str, results: List[Dict], source: str) -> str:
    """
    Format search results for display
    
    Args:
        query: Original search query
        results: List of search result dictionaries
        source: Search engine source name
    
    Returns:
        str: Formatted search results
    """
    if not results:
        return f"No search results found for query: {query}"
    
    formatted_results = f"Search results for '{query}' (via {source}):\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_results += f"{i}. **{result['title']}**\n"
        if result['url']:
            formatted_results += f"   URL: {result['url']}\n"
        formatted_results += f"   {result['snippet']}\n\n"
    
    return formatted_results.strip()


# Create the web_search tool
web_search_tool = Tool(
    name="web_search",
    description=(
        "Search the web using a hybrid approach: DuckDuckGo library (free) with Brave Search API fallback. "
        "Provides comprehensive web search results with titles, URLs, and descriptions. "
        "Automatically falls back to Brave Search if DuckDuckGo fails and BRAVE_SEARCH_API_KEY is set."
    ),
    function=web_search,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to perform"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (default: 5, max: 10)",
                "default": 5,
                "minimum": 1,
                "maximum": 10
            }
        },
        "required": ["query"]
    }
)

# Register the tool
global_tool_registry.register_tool(web_search_tool)