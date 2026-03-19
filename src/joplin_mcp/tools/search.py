from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册搜索相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def search_notes(
        query: str,
        limit: int = 100,
        page: int = 1,
        fields: str | None = None,
    ) -> dict:
        """搜索笔记

        Args:
            query: 搜索查询，支持 Joplin 搜索语法
            limit: 每页数量 (1-100)
            page: 页码
            fields: 可选，逗号分隔的返回字段
        """
        params = {
            "query": query,
            "limit": min(limit, 100),
            "page": page,
        }
        if fields:
            params["fields"] = fields

        result = await client.get("/search", params)
        return result

    @mcp.tool
    async def search_folders(
        query: str,
        limit: int = 100,
        page: int = 1,
    ) -> dict:
        """搜索笔记本

        Args:
            query: 搜索查询，支持通配符 *
            limit: 每页数量 (1-100)
            page: 页码
        """
        params = {
            "query": query,
            "type": "folder",
            "limit": min(limit, 100),
            "page": page,
        }

        result = await client.get("/search", params)
        return result

    @mcp.tool
    async def search_tags(
        query: str,
        limit: int = 100,
        page: int = 1,
    ) -> dict:
        """搜索标签

        Args:
            query: 搜索查询，支持通配符 *
            limit: 每页数量 (1-100)
            page: 页码
        """
        params = {
            "query": query,
            "type": "tag",
            "limit": min(limit, 100),
            "page": page,
        }

        result = await client.get("/search", params)
        return result
