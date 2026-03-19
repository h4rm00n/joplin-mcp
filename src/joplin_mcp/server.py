from dotenv import load_dotenv
from fastmcp import FastMCP

from joplin_mcp.config import Settings
from joplin_mcp.tools import (
    notes,
    notes_content,
    folders,
    tags,
    resources,
    search,
    todos,
    workflows,
)

load_dotenv()


def create_mcp_server(settings: Settings) -> FastMCP:
    """创建 MCP 服务器实例"""
    mcp = FastMCP(
        name=settings.server_name,
    )

    notes.register_tools(mcp, settings)
    notes_content.register_tools(mcp, settings)
    folders.register_tools(mcp, settings)
    tags.register_tools(mcp, settings)
    resources.register_tools(mcp, settings)
    search.register_tools(mcp, settings)
    todos.register_tools(mcp, settings)
    workflows.register_tools(mcp, settings)

    return mcp


settings = Settings()
mcp = create_mcp_server(settings)

if __name__ == "__main__":
    mcp.run()
