import time
from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册笔记核心操作工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def create_note(
        title: str,
        body: str | None = None,
        folder_id: str | None = None,
    ) -> dict:
        """创建普通笔记

        Args:
            title: 笔记标题
            body: 可选，Markdown 格式的笔记内容
            folder_id: 可选，指定笔记本 ID
        """
        data = {"title": title}
        if body:
            data["body"] = body
        if folder_id:
            data["parent_id"] = folder_id

        result = await client.post("/notes", data)
        return result

    @mcp.tool
    async def clip_webpage(
        url: str,
        title: str | None = None,
        folder_id: str | None = None,
    ) -> dict:
        """剪藏网页

        Args:
            url: 网页 URL
            title: 可选，笔记标题（默认使用网页标题）
            folder_id: 可选，指定笔记本 ID
        """
        data = {
            "title": title or url,
            "source_url": url,
        }
        if folder_id:
            data["parent_id"] = folder_id

        result = await client.post("/notes", data)
        return result

    @mcp.tool
    async def paste_image_note(
        title: str,
        image_data: str,
        folder_id: str | None = None,
    ) -> dict:
        """创建带图片的笔记

        Args:
            title: 笔记标题
            image_data: Base64 编码的图片数据或 Data URL
            folder_id: 可选，指定笔记本 ID
        """
        data = {
            "title": title,
            "image_data_url": image_data,
        }
        if folder_id:
            data["parent_id"] = folder_id

        result = await client.post("/notes", data)
        return result

    @mcp.tool
    async def get_note(
        note_id: str,
        include_body: bool = True,
    ) -> dict:
        """获取单个笔记详情

        Args:
            note_id: 笔记 ID
            include_body: 是否包含笔记正文（默认 True）
        """
        if include_body:
            result = await client.get(
                f"/notes/{note_id}",
                {"fields": "id,parent_id,title,body,created_time,updated_time,is_todo,todo_completed,todo_due"},
            )
        else:
            result = await client.get(
                f"/notes/{note_id}",
                {
                    "fields": "id,title,created_time,updated_time,is_todo,todo_completed,todo_due,parent_id"
                },
            )
        return result

    @mcp.tool
    async def list_notes(
        folder_id: str | None = None,
        limit: int = 10,
        sort: str = "updated",
        order: str = "desc",
    ) -> dict:
        """获取笔记列表

        Args:
            folder_id: 可选，指定笔记本 ID 过滤
            limit: 每页数量 (1-100)
            sort: 排序字段 (created, updated, title)
            order: 排序方向 (asc, desc)
        """
        params = {
            "limit": min(limit, 100),
            "order_by": f"{sort}_time" if sort in ["created", "updated"] else sort,
            "order_dir": order.upper(),
        }
        if folder_id:
            params["folder_id"] = folder_id

        result = await client.get("/notes", params)
        return result

    @mcp.tool
    async def list_recent_notes(
        hours: int = 24,
        limit: int = 10,
    ) -> dict:
        """获取最近更新的笔记

        Args:
            hours: 最近多少小时
            limit: 返回数量限制
        """
        cutoff_time = int((time.time() - hours * 3600) * 1000)
        params = {
            "limit": min(limit, 100),
            "order_by": "updated_time",
            "order_dir": "DESC",
        }
        result = await client.get("/notes", params)

        filtered = [
            note for note in result.get("items", []) if note.get("updated_time", 0) >= cutoff_time
        ]

        return {"items": filtered, "has_more": len(filtered) == limit}

    @mcp.tool
    async def move_note(note_id: str, folder_id: str) -> dict:
        """移动笔记到另一个笔记本

        Args:
            note_id: 笔记 ID
            folder_id: 目标笔记本 ID
        """
        result = await client.put(f"/notes/{note_id}", {"parent_id": folder_id})
        return result

    @mcp.tool
    async def copy_note(
        note_id: str,
        folder_id: str,
        new_title: str | None = None,
    ) -> dict:
        """复制笔记到另一个笔记本

        Args:
            note_id: 笔记 ID
            folder_id: 目标笔记本 ID
            new_title: 可选，新笔记标题（默认使用原标题）
        """
        original = await client.get(f"/notes/{note_id}")
        data = {
            "title": new_title or original.get("title"),
            "body": original.get("body", ""),
            "parent_id": folder_id,
        }
        if original.get("is_todo"):
            data["is_todo"] = "1"
        if original.get("todo_due"):
            data["todo_due"] = str(original.get("todo_due"))

        result = await client.post("/notes", data)
        return result

    @mcp.tool
    async def trash_note(note_id: str) -> dict:
        """将笔记移至回收站

        Args:
            note_id: 笔记 ID
        """
        result = await client.delete(f"/notes/{note_id}", permanent=False)
        return result

    @mcp.tool
    async def restore_note(note_id: str) -> dict:
        """从回收站恢复笔记

        Args:
            note_id: 笔记 ID
        """
        result = await client.put(f"/notes/{note_id}", {"deleted_time": "0"})
        return result

    @mcp.tool
    async def permanently_delete_note(note_id: str) -> dict:
        """永久删除笔记

        Args:
            note_id: 笔记 ID
        """
        result = await client.delete(f"/notes/{note_id}", permanent=True)
        return result

    @mcp.tool
    async def archive_note(note_id: str, archive_folder_id: str) -> dict:
        """归档笔记（移动到归档笔记本）

        Args:
            note_id: 笔记 ID
            archive_folder_id: 归档笔记本 ID
        """
        result = await client.put(f"/notes/{note_id}", {"parent_id": archive_folder_id})
        return result
