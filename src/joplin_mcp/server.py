from fastmcp import FastMCP

from .config import Settings
from .tools import notes, folders, tags, resources, search


def create_mcp_server(settings: Settings) -> FastMCP:
    """创建 MCP 服务器实例"""
    mcp = FastMCP(
        name=settings.server_name,
    )

    notes.register_tools(mcp, settings)
    folders.register_tools(mcp, settings)
    tags.register_tools(mcp, settings)
    resources.register_tools(mcp, settings)
    search.register_tools(mcp, settings)

    return mcp


settings = Settings()
mcp = create_mcp_server(settings)

if __name__ == "__main__":
    mcp.run()
