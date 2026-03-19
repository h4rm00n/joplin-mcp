from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册标签相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def list_tags(
        limit: int = 100,
        page: int = 1,
        order_by: str = "title",
        order_dir: str = "ASC",
    ) -> dict:
        """获取所有标签

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

        result = await client.get("/tags", params)
        return result

    @mcp.tool
    async def get_tag(tag_id: str) -> dict:
        """获取单个标签详情

        Args:
            tag_id: 标签 ID
        """
        result = await client.get(f"/tags/{tag_id}")
        return result

    @mcp.tool
    async def create_tag(title: str, parent_id: str | None = None) -> dict:
        """创建新标签

        Args:
            title: 标签标题
            parent_id: 可选，父标签 ID（用于创建子标签）
        """
        data = {"title": title}
        if parent_id:
            data["parent_id"] = parent_id

        result = await client.post("/tags", data)
        return result

    @mcp.tool
    async def update_tag(tag_id: str, **kwargs) -> dict:
        """更新标签属性

        Args:
            tag_id: 标签 ID
            kwargs: 要更新的属性，如 title 等
        """
        result = await client.put(f"/tags/{tag_id}", kwargs)
        return result

    @mcp.tool
    async def delete_tag(tag_id: str, permanent: bool = False) -> dict:
        """删除标签

        Args:
            tag_id: 标签 ID
            permanent: 是否永久删除
        """
        result = await client.delete(f"/tags/{tag_id}", permanent=permanent)
        return result

    @mcp.tool
    async def get_tag_notes(tag_id: str) -> dict:
        """获取具有此标签的所有笔记

        Args:
            tag_id: 标签 ID
        """
        result = await client.get(f"/tags/{tag_id}/notes")
        return result

    @mcp.tool
    async def add_tag_to_note(tag_id: str, note_id: str) -> dict:
        """为笔记添加标签

        Args:
            tag_id: 标签 ID
            note_id: 笔记 ID
        """
        data = {"id": note_id}
        result = await client.post(f"/tags/{tag_id}/notes", data)
        return result

    @mcp.tool
    async def remove_tag_from_note(tag_id: str, note_id: str) -> dict:
        """从笔记移除标签

        Args:
            tag_id: 标签 ID
            note_id: 笔记 ID
        """
        result = await client.delete(f"/tags/{tag_id}/notes/{note_id}")
        return result
