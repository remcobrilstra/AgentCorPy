"""
Web tools for the AgentCorp framework
"""

from typing import Dict, Any
import html2text
from requests_html import HTMLSession

from ...tool_registry import Tool, global_tool_registry, ToolExecutionContext


def web_fetch(context: ToolExecutionContext, url: str, render_js: bool = False) -> str:
    """
    Fetch content from a URL and return it as markdown.
    Optionally supports client-side rendered sites by executing JavaScript.

    Args:
        context: Tool execution context
        url: The URL to fetch content from
        render_js: Whether to render JavaScript (requires Chromium)

    Returns:
        str: The page content converted to markdown format
    """
    try:
        if render_js:
            # Use requests-html for JavaScript rendering
            session = HTMLSession()

            # Fetch the page
            response = session.get(url)

            # Render JavaScript (this executes any client-side rendering)
            response.html.render(timeout=20)  # 20 second timeout for JS execution

            # Convert HTML to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False  # Keep links in markdown format
            h.ignore_images = False  # Keep images in markdown format
            h.ignore_tables = False  # Keep tables in markdown format
            h.wrap_links = False  # Don't wrap links
            h.wrap_list_items = True  # Wrap list items
            h.ul_item_mark = '-'  # Use - for unordered lists
            h.emphasis_mark = '*'  # Use * for emphasis

            # Convert to markdown
            markdown_content = h.handle(response.html.html)
        else:
            # Use simple requests for static content
            import requests
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Convert HTML to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_tables = False
            h.wrap_links = False
            h.wrap_list_items = True
            h.ul_item_mark = '-'
            h.emphasis_mark = '*'

            markdown_content = h.handle(response.text)

        return markdown_content

    except Exception as e:
        return f"Error fetching URL {url}: {str(e)}"


# Create the web_fetch tool
web_fetch_tool = Tool(
    name="web_fetch",
    description="Fetch content from a URL and return it as markdown. Supports client-side rendered sites by executing JavaScript when render_js=true.",
    function=web_fetch,
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch content from"
            },
            "render_js": {
                "type": "boolean",
                "description": "Whether to render JavaScript for client-side content (default: false)",
                "default": False
            }
        },
        "required": ["url"]
    }
)

# Register the tool
global_tool_registry.register_tool(web_fetch_tool)