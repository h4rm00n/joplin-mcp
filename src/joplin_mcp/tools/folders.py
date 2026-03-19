from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册笔记本相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def list_folders() -> dict:
        """获取笔记本列表（树形结构）

        返回嵌套的笔记本树形结构，子笔记本在 children 键下
        """
        result = await client.get("/folders")
        return result

    @mcp.tool
    async def get_folder(folder_id: str) -> dict:
        """获取单个笔记本详情

        Args:
            folder_id: 笔记本 ID
        """
        result = await client.get(f"/folders/{folder_id}")
        return result

    @mcp.tool
    async def create_folder(title: str, parent_id: str | None = None) -> dict:
        """创建新笔记本

        Args:
            title: 笔记本标题
            parent_id: 可选，父笔记本 ID（用于创建子笔记本）
        """
        data = {"title": title}
        if parent_id:
            data["parent_id"] = parent_id

        result = await client.post("/folders", data)
        return result

    @mcp.tool
    async def update_folder(folder_id: str, **kwargs) -> dict:
        """更新笔记本属性

        Args:
            folder_id: 笔记本 ID
            kwargs: 要更新的属性，如 title, icon 等
        """
        result = await client.put(f"/folders/{folder_id}", kwargs)
        return result

    @mcp.tool
    async def delete_folder(folder_id: str, permanent: bool = False) -> dict:
        """删除笔记本

        Args:
            folder_id: 笔记本 ID
            permanent: 是否永久删除（默认移至回收站）
        """
        result = await client.delete(f"/folders/{folder_id}", permanent=permanent)
        return result

    @mcp.tool
    async def get_folder_notes(
        folder_id: str,
        limit: int = 10,
        page: int = 1,
        order_by: str = "updated_time",
        order_dir: str = "DESC",
    ) -> dict:
        """获取笔记本内的笔记列表

        Args:
            folder_id: 笔记本 ID
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

        result = await client.get(f"/folders/{folder_id}/notes", params)
        return result
