import httpx
import json
from typing import Optional, Any

from .exceptions import JoplinConnectionError, JoplinAuthError, JoplinNotFoundError


class JoplinClient:
    """Joplin REST API 客户端封装"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self._client = httpx.AsyncClient(
            base_url=base_url,
            params={"token": token},
            timeout=30.0,
        )

    async def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """GET 请求"""
        try:
            response = await self._client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise JoplinConnectionError(f"无法连接到 Joplin: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise JoplinAuthError(f"认证失败：{e}")
            elif e.response.status_code == 404:
                raise JoplinNotFoundError(f"资源未找到：{e}")
            raise
        except json.JSONDecodeError as e:
            raise JoplinConnectionError(f"无效的 JSON 响应：{e}")

    async def post(self, endpoint: str, data: dict) -> Any:
        """POST 请求"""
        try:
            response = await self._client.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise JoplinConnectionError(f"无法连接到 Joplin: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise JoplinAuthError(f"认证失败：{e}")
            elif e.response.status_code == 404:
                raise JoplinNotFoundError(f"资源未找到：{e}")
            raise
        except json.JSONDecodeError as e:
            raise JoplinConnectionError(f"无效的 JSON 响应：{e}")

    async def put(self, endpoint: str, data: dict) -> Any:
        """PUT 请求"""
        try:
            response = await self._client.put(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise JoplinConnectionError(f"无法连接到 Joplin: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise JoplinAuthError(f"认证失败：{e}")
            elif e.response.status_code == 404:
                raise JoplinNotFoundError(f"资源未找到：{e}")
            raise
        except json.JSONDecodeError as e:
            raise JoplinConnectionError(f"无效的 JSON 响应：{e}")

    async def delete(self, endpoint: str, permanent: bool = False) -> Any:
        """DELETE 请求"""
        params = {"permanent": "1"} if permanent else {}
        try:
            response = await self._client.delete(endpoint, params=params)
            response.raise_for_status()
            # DELETE 操作可能返回空响应体
            content = response.content
            if not content or content.strip() == b"":
                return {}
            return response.json()
        except httpx.ConnectError as e:
            raise JoplinConnectionError(f"无法连接到 Joplin: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise JoplinAuthError(f"认证失败：{e}")
            elif e.response.status_code == 404:
                raise JoplinNotFoundError(f"资源未找到：{e}")
            raise
        except json.JSONDecodeError as e:
            raise JoplinConnectionError(f"无效的 JSON 响应：{e}")

    async def ping(self) -> bool:
        """检查 Joplin 服务是否可用"""
        try:
            response = await self._client.get("/ping")
            return response.text == "JoplinClipperServer"
        except httpx.ConnectError:
            return False

    async def close(self):
        """关闭客户端连接"""
        await self._client.aclose()
