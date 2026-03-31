from __future__ import annotations

from app.tools.base import Tool, ToolResult


class WebSearchTool(Tool):
    """Stubbed web search tool for future implementation."""

    name = "web_search"
    description = "Search the web for evidence, data, and sources to support arguments."

    async def execute(self, **kwargs) -> ToolResult:
        # Stub: return placeholder indicating this tool is not yet implemented
        query = kwargs.get("query", "")
        return ToolResult(
            success=False,
            error=f"Web search is not yet implemented. Query was: '{query}'. "
            "This tool will be available in a future version with RAG integration.",
        )
