from __future__ import annotations

from app.agent.state import SessionState
from app.tools.base import Tool, ToolResult


class WorkspaceTool(Tool):
    """Manages the evolving persuasive statement draft within a session."""

    name = "workspace"
    description = "Read, update, and track revisions of the persuasive statement draft."

    def __init__(self, state: SessionState):
        self.state = state

    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "get")

        if action == "get":
            return ToolResult(
                success=True,
                data={
                    "draft": self.state.current_draft,
                    "revision_count": len(self.state.revision_history),
                },
            )
        elif action == "update":
            new_draft = kwargs.get("draft")
            if not new_draft:
                return ToolResult(success=False, error="No draft content provided.")
            if self.state.current_draft:
                self.state.revision_history.append(self.state.current_draft)
            self.state.current_draft = new_draft
            return ToolResult(success=True, data={"draft": new_draft})
        elif action == "history":
            return ToolResult(
                success=True,
                data={"revisions": self.state.revision_history},
            )
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")
