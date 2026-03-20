from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册笔记本相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def list_folders(as_tree: bool = False) -> dict:
        """获取笔记本列表

        Args:
            as_tree: 是否返回树形结构（默认 False 返回扁平列表）
        """
        if as_tree:
            folders = await client.get("/folders")
            tree = build_folder_tree(folders.get("items", []))
            return {"items": tree}
        else:
            result = await client.get("/folders")
            return result

    def build_folder_tree(folders: list) -> list:
        """将扁平的笔记本列表转换为树形结构"""
        folder_map = {f["id"]: {**f, "children": []} for f in folders}
        root_folders = []

        for folder in folder_map.values():
            parent_id = folder.get("parent_id")
            if parent_id:
                parent = folder_map.get(parent_id)
                if parent:
                    parent["children"].append(folder)
            else:
                root_folders.append(folder)

        return root_folders

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
        """创建笔记本

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
    async def create_subfolder(parent_id: str, title: str) -> dict:
        """创建子笔记本

        Args:
            parent_id: 父笔记本 ID
            title: 子笔记本标题
        """
        data = {"title": title, "parent_id": parent_id}
        result = await client.post("/folders", data)
        return result

    @mcp.tool
    async def rename_folder(folder_id: str, title: str) -> dict:
        """重命名笔记本

        Args:
            folder_id: 笔记本 ID
            title: 新标题
        """
        result = await client.put(f"/folders/{folder_id}", {"title": title})
        return result

    @mcp.tool
    async def move_folder(folder_id: str, new_parent_id: str | None = None) -> dict:
        """移动笔记本

        Args:
            folder_id: 笔记本 ID
            new_parent_id: 新父笔记本 ID（None 表示移到根目录）
        """
        data = {"parent_id": new_parent_id} if new_parent_id else {"parent_id": ""}
        result = await client.put(f"/folders/{folder_id}", data)
        return result

    @mcp.tool
    async def set_folder_icon(folder_id: str, icon: str) -> dict:
        """设置笔记本图标 emoji

        Args:
            folder_id: 笔记本 ID
            icon: Emoji 图标
        """
        result = await client.put(f"/folders/{folder_id}", {"icon": icon})
        return result

    @mcp.tool
    async def get_folder_tree() -> dict:
        """获取完整的笔记本树形结构

        返回嵌套的笔记本树形结构
        """
        folders = await client.get("/folders")
        tree = build_folder_tree(folders.get("items", []))
        return {"items": tree}

    @mcp.tool
    async def get_folder_notes(
        folder_id: str,
        limit: int = 10,
        sort: str = "updated",
        order: str = "desc",
    ) -> dict:
        """获取笔记本内的笔记列表

        Args:
            folder_id: 笔记本 ID
            limit: 每页数量 (1-100)
            sort: 排序字段 (created, updated, title)
            order: 排序方向 (asc, desc)
        """
        params = {
            "limit": min(limit, 100),
            "order_by": f"{sort}_time" if sort in ["created", "updated"] else sort,
            "order_dir": order.upper(),
        }

        result = await client.get(f"/folders/{folder_id}/notes", params)
        return result

    @mcp.tool
    async def trash_folder(folder_id: str) -> dict:
        """将笔记本移至回收站

        Args:
            folder_id: 笔记本 ID
        """
        result = await client.delete(f"/folders/{folder_id}", permanent=False)
        return result

    @mcp.tool
    async def restore_folder(folder_id: str) -> dict:
        """从回收站恢复笔记本

        Args:
            folder_id: 笔记本 ID
        """
        result = await client.put(f"/folders/{folder_id}", {"deleted_time": "0"})
        return result

    @mcp.tool
    async def permanently_delete_folder(folder_id: str) -> dict:
        """永久删除笔记本

        Args:
            folder_id: 笔记本 ID
        """
        result = await client.delete(f"/folders/{folder_id}", permanent=True)
        return result
