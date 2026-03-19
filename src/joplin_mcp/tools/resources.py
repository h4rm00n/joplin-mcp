from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册资源相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def list_resources(
        limit: int = 100,
        page: int = 1,
        order_by: str = "title",
        order_dir: str = "ASC",
    ) -> dict:
        """获取资源列表

        Args:
            limit: 每页数量 (1-100)
            page: 页码
            order_by: 排序字段
            order_dir: 排序方向 (ASC, DESC)
        """
        params = {
            "limit": min(limit, 100),
            "page": page,
            "order_by": order_by,
            "order_dir": order_dir,
        }

        result = await client.get("/resources", params)
        return result

    @mcp.tool
    async def get_resource(resource_id: str) -> dict:
        """获取资源详情

        Args:
            resource_id: 资源 ID
        """
        result = await client.get(f"/resources/{resource_id}")
        return result

    @mcp.tool
    async def get_resource_file(resource_id: str) -> bytes:
        """下载资源文件

        Args:
            resource_id: 资源 ID

        返回文件的二进制内容
        """
        response = await client._client.get(f"/resources/{resource_id}/file")
        response.raise_for_status()
        return response.content

    @mcp.tool
    async def get_resource_notes(resource_id: str) -> dict:
        """获取与资源关联的笔记

        Args:
            resource_id: 资源 ID
        """
        result = await client.get(f"/resources/{resource_id}/notes")
        return result

    @mcp.tool
    async def delete_resource(resource_id: str, permanent: bool = False) -> dict:
        """删除资源

        Args:
            resource_id: 资源 ID
            permanent: 是否永久删除
        """
        result = await client.delete(f"/resources/{resource_id}", permanent=permanent)
        return result
