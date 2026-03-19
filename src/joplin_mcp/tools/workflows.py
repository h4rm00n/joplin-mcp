import time
from datetime import datetime, timedelta
from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册复合工作流工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def batch_move_notes(note_ids: list[str], folder_id: str) -> dict:
        """批量移动笔记

        Args:
            note_ids: 笔记 ID 列表
            folder_id: 目标笔记本 ID
        """
        results = []
        for note_id in note_ids:
            await client.put(f"/notes/{note_id}", {"parent_id": folder_id})
            results.append({"note_id": note_id, "success": True})

        return {"moved_count": len(results), "results": results}

    @mcp.tool
    async def batch_delete_notes(
        note_ids: list[str],
        permanent: bool = False,
    ) -> dict:
        """批量删除笔记

        Args:
            note_ids: 笔记 ID 列表
            permanent: 是否永久删除
        """
        results = []
        for note_id in note_ids:
            await client.delete(f"/notes/{note_id}", permanent=permanent)
            results.append({"note_id": note_id, "success": True})

        return {"deleted_count": len(results), "results": results}

    @mcp.tool
    async def batch_add_tag(tag_id: str, note_ids: list[str]) -> dict:
        """批量为笔记添加标签

        Args:
            tag_id: 标签 ID
            note_ids: 笔记 ID 列表
        """
        results = []
        for note_id in note_ids:
            await client.post(f"/tags/{tag_id}/notes", {"id": note_id})
            results.append({"note_id": note_id, "success": True})

        return {"tagged_count": len(results), "results": results}

    @mcp.tool
    async def batch_complete_todos(note_ids: list[str]) -> dict:
        """批量完成待办

        Args:
            note_ids: 待办事项 ID 列表
        """
        results = []
        current_time = int(time.time() * 1000)
        for note_id in note_ids:
            await client.put(f"/notes/{note_id}", {"todo_completed": str(current_time)})
            results.append({"note_id": note_id, "success": True})

        return {"completed_count": len(results), "results": results}

    @mcp.tool
    async def inbox_to_folder(note_id: str, target_folder_id: str) -> dict:
        """将笔记从收件箱整理到目标文件夹

        Args:
            note_id: 笔记 ID
            target_folder_id: 目标笔记本 ID
        """
        await client.put(f"/notes/{note_id}", {"parent_id": target_folder_id})
        return {"note_id": note_id, "folder_id": target_folder_id, "success": True}

    @mcp.tool
    async def process_todo(note_id: str, action: str) -> dict:
        """处理待办（完成/延期/转笔记）

        Args:
            note_id: 待办事项 ID
            action: 操作类型 (complete, convert_to_note, postpone_1d, postpone_1w)
        """
        if action == "complete":
            await client.put(f"/notes/{note_id}", {"todo_completed": str(int(time.time() * 1000))})
        elif action == "convert_to_note":
            await client.put(
                f"/notes/{note_id}",
                {
                    "is_todo": "0",
                    "todo_completed": "0",
                    "todo_due": "0",
                },
            )
        elif action == "postpone_1d":
            due_time = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
            await client.put(f"/notes/{note_id}", {"todo_due": str(due_time)})
        elif action == "postpone_1w":
            due_time = int((datetime.now() + timedelta(weeks=1)).timestamp() * 1000)
            await client.put(f"/notes/{note_id}", {"todo_due": str(due_time)})
        else:
            raise ValueError(f"未知操作：{action}")

        return {"note_id": note_id, "action": action, "success": True}

    @mcp.tool
    async def daily_review(date: str | None = None) -> dict:
        """获取指定日期的笔记回顾

        Args:
            date: 日期 (YYYY-MM-DD 格式，默认今天)
        """
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()

        start_time = int(target_date.replace(hour=0, minute=0, second=0).timestamp() * 1000)
        end_time = int(target_date.replace(hour=23, minute=59, second=59).timestamp() * 1000)

        notes = await client.get(
            "/notes",
            {
                "limit": "100",
                "order_by": "updated_time",
                "order_dir": "ASC",
            },
        )

        filtered = [
            note
            for note in notes.get("items", [])
            if start_time <= note.get("updated_time", 0) <= end_time
        ]

        todos = [note for note in filtered if note.get("is_todo")]
        completed_todos = [t for t in todos if t.get("todo_completed")]

        return {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "total_notes": len(filtered),
            "todos": {
                "total": len(todos),
                "completed": len(completed_todos),
                "pending": len(todos) - len(completed_todos),
            },
            "notes": filtered,
        }

    @mcp.tool
    async def weekly_review(week_start_date: str | None = None) -> dict:
        """获取本周笔记回顾

        Args:
            week_start_date: 周一日期 (YYYY-MM-DD 格式，默认本周一)
        """
        if week_start_date:
            start = datetime.strptime(week_start_date, "%Y-%m-%d")
        else:
            today = datetime.now()
            start = today - timedelta(days=today.weekday())

        start = start.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=7)

        start_time = int(start.timestamp() * 1000)
        end_time = int(end.timestamp() * 1000)

        notes = await client.get(
            "/notes",
            {
                "limit": "100",
                "order_by": "updated_time",
                "order_dir": "ASC",
            },
        )

        filtered = [
            note
            for note in notes.get("items", [])
            if start_time <= note.get("updated_time", 0) <= end_time
        ]

        todos = [note for note in filtered if note.get("is_todo")]
        completed_todos = [t for t in todos if t.get("todo_completed")]

        folders = await client.get("/folders")
        folder_map = {f["id"]: f["title"] for f in folders.get("items", [])}

        by_folder = {}
        for note in filtered:
            folder_id = note.get("parent_id", "root")
            folder_name = folder_map.get(folder_id, "未分类")
            if folder_name not in by_folder:
                by_folder[folder_name] = 0
            by_folder[folder_name] += 1

        return {
            "week_start": start.strftime("%Y-%m-%d"),
            "week_end": (end - timedelta(days=1)).strftime("%Y-%m-%d"),
            "total_notes": len(filtered),
            "todos": {
                "total": len(todos),
                "completed": len(completed_todos),
                "pending": len(todos) - len(completed_todos),
            },
            "by_folder": by_folder,
            "notes": filtered,
        }
