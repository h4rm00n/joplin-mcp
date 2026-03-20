import time
from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册待办任务相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def create_todo(
        title: str,
        body: str | None = None,
        due_date: str | None = None,
        folder_id: str | None = None,
    ) -> dict:
        """创建待办事项

        Args:
            title: 待办标题
            body: 可选，待办详情
            due_date: 可选，截止日期 (YYYY-MM-DD 格式)
            folder_id: 可选，指定笔记本 ID
        """
        data = {
            "title": title,
            "is_todo": "1",
        }
        if body:
            data["body"] = body
        if due_date:
            parsed = time.strptime(due_date, "%Y-%m-%d")
            data["todo_due"] = str(int(time.mktime(parsed) * 1000))
        if folder_id:
            data["parent_id"] = folder_id

        result = await client.post("/notes", data)
        return result

    @mcp.tool
    async def complete_todo(note_id: str) -> dict:
        """标记待办为已完成

        Args:
            note_id: 待办事项 ID
        """
        result = await client.put(f"/notes/{note_id}", {"todo_completed": int(time.time() * 1000)})
        return result

    @mcp.tool
    async def uncomplete_todo(note_id: str) -> dict:
        """取消完成待办

        Args:
            note_id: 待办事项 ID
        """
        result = await client.put(f"/notes/{note_id}", {"todo_completed": "0"})
        return result

    @mcp.tool
    async def set_todo_due(note_id: str, due_date: str) -> dict:
        """设置待办截止时间

        Args:
            note_id: 待办事项 ID
            due_date: 截止日期 (YYYY-MM-DD 格式)
        """
        parsed = time.strptime(due_date, "%Y-%m-%d")
        result = await client.put(
            f"/notes/{note_id}", {"todo_due": str(int(time.mktime(parsed) * 1000))}
        )
        return result

    @mcp.tool
    async def clear_todo_due(note_id: str) -> dict:
        """清除待办截止时间

        Args:
            note_id: 待办事项 ID
        """
        result = await client.put(f"/notes/{note_id}", {"todo_due": "0"})
        return result

    @mcp.tool
    async def list_todos(
        status: str | None = None,
        folder_id: str | None = None,
        limit: int = 10,
        page: int = 1,
        order_by: str = "updated_time",
        order_dir: str = "DESC",
    ) -> dict:
        """获取待办列表

        Args:
            status: 筛选状态 (all, active, completed)
            folder_id: 可选，指定笔记本 ID 过滤
            limit: 每页数量 (1-100)
            page: 页码
            order_by: 排序字段
            order_dir: 排序方向 (ASC, DESC)
        """
        params = {
            "is_todo": "1",
            "limit": min(limit, 100),
            "page": page,
            "order_by": order_by,
            "order_dir": order_dir,
        }
        if folder_id:
            params["folder_id"] = folder_id
        if status == "active":
            params["todo_completed"] = "0"
        elif status == "completed":
            params["todo_completed"] = "1"

        result = await client.get("/notes", params)
        return result
