from __future__ import annotations

from app.tools.base import Tool, ToolResult


class DocumentRetrievalTool(Tool):
    """Stubbed document retrieval tool for future RAG implementation."""

    name = "document_retrieval"
    description = "Retrieve relevant documents and passages from a knowledge base."

    async def execute(self, **kwargs) -> ToolResult:
        # Stub: return placeholder indicating this tool is not yet implemented
        query = kwargs.get("query", "")
        return ToolResult(
            success=False,
            error=f"Document retrieval is not yet implemented. Query was: '{query}'. "
            "This tool will be available in a future version with RAG integration.",
        )
