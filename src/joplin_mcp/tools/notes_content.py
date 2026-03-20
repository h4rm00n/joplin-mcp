from fastmcp import FastMCP

from ..client import JoplinClient
from ..config import Settings


def register_tools(mcp: FastMCP, settings: Settings):
    """注册笔记内容编辑相关工具"""
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)

    @mcp.tool
    async def update_note_title(note_id: str, title: str) -> dict:
        """仅更新笔记标题

        Args:
            note_id: 笔记 ID
            title: 新标题
        """
        result = await client.put(f"/notes/{note_id}", {"title": title})
        return result

    @mcp.tool
    async def update_note_body(note_id: str, body: str) -> dict:
        """仅更新笔记正文

        Args:
            note_id: 笔记 ID
            body: Markdown 格式的新内容
        """
        result = await client.put(f"/notes/{note_id}", {"body": body})
        return result

    @mcp.tool
    async def append_to_note(
        note_id: str,
        content: str,
        as_html: bool = False,
    ) -> dict:
        """追加内容到笔记末尾

        Args:
            note_id: 笔记 ID
            content: 要追加的内容
            as_html: 是否为 HTML 格式（默认 Markdown）
        """
        note = await client.get(f"/notes/{note_id}", {"fields": "body,body_html"})

        if as_html:
            new_body_html = (note.get("body_html") or "") + content
            result = await client.put(f"/notes/{note_id}", {"body_html": new_body_html})
        else:
            new_body = (note.get("body") or "") + "\n" + content
            result = await client.put(f"/notes/{note_id}", {"body": new_body})

        return result

    @mcp.tool
    async def prepend_to_note(
        note_id: str,
        content: str,
        as_html: bool = False,
    ) -> dict:
        """在笔记开头添加内容

        Args:
            note_id: 笔记 ID
            content: 要添加的内容
            as_html: 是否为 HTML 格式（默认 Markdown）
        """
        note = await client.get(f"/notes/{note_id}", {"fields": "body,body_html"})

        if as_html:
            new_body_html = content + (note.get("body_html") or "")
            result = await client.put(f"/notes/{note_id}", {"body_html": new_body_html})
        else:
            new_body = content + "\n" + (note.get("body") or "")
            result = await client.put(f"/notes/{note_id}", {"body": new_body})

        return result

    @mcp.tool
    async def replace_in_note(
        note_id: str,
        search: str,
        replace: str,
    ) -> dict:
        """替换笔记中的文本

        Args:
            note_id: 笔记 ID
            search: 要查找的文本
            replace: 替换的文本
        """
        note = await client.get(f"/notes/{note_id}", {"fields": "body"})
        current_body = note.get("body", "")
        new_body = current_body.replace(search, replace)

        result = await client.put(f"/notes/{note_id}", {"body": new_body})
        return result
