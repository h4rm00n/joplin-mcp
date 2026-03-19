from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册标签相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def list_tags(
        limit: int = 100,
        sort: str = "title",
        order: str = "asc",
    ) -> dict:
        """获取所有标签

        Args:
            limit: 每页数量 (1-100)
            sort: 排序字段 (title, created_time)
            order: 排序方向 (asc, desc)
        """
        params = {
            "limit": min(limit, 100),
            "order_by": sort,
            "order_dir": order.upper(),
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
        """创建标签

        Args:
            title: 标签标题
            parent_id: 可选，父标签 ID（用于创建层级标签）
        """
        data = {"title": title}
        if parent_id:
            data["parent_id"] = parent_id

        result = await client.post("/tags", data)
        return result

    @mcp.tool
    async def rename_tag(tag_id: str, title: str) -> dict:
        """重命名标签

        Args:
            tag_id: 标签 ID
            title: 新标题
        """
        result = await client.put(f"/tags/{tag_id}", {"title": title})
        return result

    @mcp.tool
    async def merge_tags(
        source_tag_ids: list[str],
        target_tag_id: str,
    ) -> dict:
        """合并多个标签到一个

        Args:
            source_tag_ids: 源标签 ID 列表
            target_tag_id: 目标标签 ID
        """
        results = []
        for source_id in source_tag_ids:
            notes = await client.get(f"/tags/{source_id}/notes")
            for note in notes.get("items", []):
                await client.post(f"/tags/{target_tag_id}/notes", {"id": note["id"]})
                await client.delete(f"/tags/{source_id}/notes/{note['id']}")
            results.append(await client.delete(f"/tags/{source_id}"))

        return {"merged_count": len(source_tag_ids), "target_tag_id": target_tag_id}

    @mcp.tool
    async def trash_tag(tag_id: str) -> dict:
        """删除标签

        Args:
            tag_id: 标签 ID
        """
        result = await client.delete(f"/tags/{tag_id}", permanent=False)
        return result

    @mcp.tool
    async def get_tag_notes(tag_id: str, limit: int = 10) -> dict:
        """获取具有某标签的所有笔记

        Args:
            tag_id: 标签 ID
            limit: 返回数量限制
        """
        params = {"limit": min(limit, 100)}
        result = await client.get(f"/tags/{tag_id}/notes", params)
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

    @mcp.tool
    async def set_note_tags(note_id: str, tag_ids: list[str]) -> dict:
        """设置笔记的标签（替换现有）

        Args:
            note_id: 笔记 ID
            tag_ids: 标签 ID 列表
        """
        current_tags = await client.get(f"/notes/{note_id}/tags")
        for tag in current_tags.get("items", []):
            await client.delete(f"/tags/{tag['id']}/notes/{note_id}")

        for tag_id in tag_ids:
            await client.post(f"/tags/{tag_id}/notes", {"id": note_id})

        return {"note_id": note_id, "tag_ids": tag_ids}

    @mcp.tool
    async def get_note_tags(note_id: str) -> dict:
        """获取笔记的所有标签

        Args:
            note_id: 笔记 ID
        """
        result = await client.get(f"/notes/{note_id}/tags")
        return result
