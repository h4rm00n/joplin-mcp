from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册笔记相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def list_notes(
        folder_id: str | None = None,
        limit: int = 10,
        page: int = 1,
        order_by: str = "updated_time",
        order_dir: str = "DESC",
        include_deleted: bool = False,
        include_conflicts: bool = False,
    ) -> dict:
        """获取笔记列表

        Args:
            folder_id: 可选，指定笔记本 ID 过滤
            limit: 每页数量 (1-100)
            page: 页码
            order_by: 排序字段 (created_time, updated_time, title 等)
            order_dir: 排序方向 (ASC, DESC)
            include_deleted: 是否包含回收站中的笔记
            include_conflicts: 是否包含冲突笔记
        """
        params = {
            "limit": min(limit, 100),
            "page": page,
            "order_by": order_by,
            "order_dir": order_dir,
        }
        if folder_id:
            params["folder_id"] = folder_id
        if include_deleted:
            params["include_deleted"] = "1"
        if include_conflicts:
            params["include_conflicts"] = "1"

        result = await client.get("/notes", params)
        return result

    @mcp.tool
    async def get_note(note_id: str, fields: str | None = None) -> dict:
        """获取单个笔记详情

        Args:
            note_id: 笔记 ID
            fields: 可选，逗号分隔的字段列表，如 "title,body,created_time"
        """
        params = {}
        if fields:
            params["fields"] = fields

        result = await client.get(f"/notes/{note_id}", params)
        return result

    @mcp.tool
    async def create_note(
        title: str,
        body: str | None = None,
        body_html: str | None = None,
        folder_id: str | None = None,
        image_data_url: str | None = None,
        is_todo: bool = False,
        todo_due: int | None = None,
    ) -> dict:
        """创建新笔记

        Args:
            title: 笔记标题
            body: Markdown 格式的笔记内容
            body_html: HTML 格式的笔记内容（与 body 二选一）
            folder_id: 可选，指定笔记本 ID
            image_data_url: 可选，Data URL 格式的图像
            is_todo: 是否为待办事项
            todo_due: 待办事项到期时间（毫秒时间戳）
        """
        data = {"title": title}
        if body:
            data["body"] = body
        if body_html:
            data["body_html"] = body_html
        if folder_id:
            data["parent_id"] = folder_id
        if image_data_url:
            data["image_data_url"] = image_data_url
        if is_todo:
            data["is_todo"] = "1"
        if todo_due:
            data["todo_due"] = str(todo_due)

        result = await client.post("/notes", data)
        return result

    @mcp.tool
    async def update_note(
        note_id: str,
        title: str | None = None,
        body: str | None = None,
        body_html: str | None = None,
        is_todo: bool | None = None,
        todo_due: int | None = None,
        todo_completed: int | None = None,
        folder_id: str | None = None,
    ) -> dict:
        """更新笔记属性

        Args:
            note_id: 笔记 ID
            title: 笔记标题
            body: Markdown 格式的笔记内容
            body_html: HTML 格式的笔记内容
            is_todo: 是否为待办事项
            todo_due: 待办事项到期时间（毫秒时间戳）
            todo_completed: 待办事项完成时间（毫秒时间戳）
            folder_id: 笔记本 ID
        """
        data = {}
        if title is not None:
            data["title"] = title
        if body is not None:
            data["body"] = body
        if body_html is not None:
            data["body_html"] = body_html
        if is_todo is not None:
            data["is_todo"] = "1" if is_todo else "0"
        if todo_due is not None:
            data["todo_due"] = str(todo_due)
        if todo_completed is not None:
            data["todo_completed"] = str(todo_completed)
        if folder_id is not None:
            data["parent_id"] = folder_id

        result = await client.put(f"/notes/{note_id}", data)
        return result

    @mcp.tool
    async def delete_note(note_id: str, permanent: bool = False) -> dict:
        """删除笔记

        Args:
            note_id: 笔记 ID
            permanent: 是否永久删除（默认移至回收站）
        """
        result = await client.delete(f"/notes/{note_id}", permanent=permanent)
        return result

    @mcp.tool
    async def get_note_tags(note_id: str) -> dict:
        """获取笔记的标签

        Args:
            note_id: 笔记 ID
        """
        result = await client.get(f"/notes/{note_id}/tags")
        return result

    @mcp.tool
    async def get_note_resources(note_id: str) -> dict:
        """获取笔记的附件资源

        Args:
            note_id: 笔记 ID
        """
        result = await client.get(f"/notes/{note_id}/resources")
        return result

    @mcp.tool
    async def delete_note_revisions(note_id: str) -> dict:
        """删除笔记的所有修订版本

        Args:
            note_id: 笔记 ID
        """
        result = await client.delete(f"/notes/{note_id}/revisions")
        return result
