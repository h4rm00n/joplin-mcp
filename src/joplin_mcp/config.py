from typing import Any
from pydantic import Field
from pydantic_settings import BaseSettings


class JoplinSettings(BaseSettings):
    """Joplin API 配置"""

    host: str = Field(default="localhost", description="Joplin 主机")
    port: int = Field(default=41184, description="Joplin 端口")
    token: str = Field(..., description="Joplin API Token")

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    class Config:
        env_prefix = "JOPLIN__"


class Settings(BaseSettings):
    """MCP 服务器配置"""

    joplin: JoplinSettings = Field(default_factory=lambda: JoplinSettings())  # type: ignore
    server_name: str = "Joplin"
    debug: bool = False

    class Config:
        env_prefix = "JOPLIN_MCP_"
        env_nested_delimiter = "__"
