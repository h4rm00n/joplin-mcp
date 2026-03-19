class JoplinMCPError(Exception):
    """基础异常类"""

    pass


class JoplinConnectionError(JoplinMCPError):
    """Joplin 连接失败"""

    pass


class JoplinAuthError(JoplinMCPError):
    """认证失败（Token 无效）"""

    pass


class JoplinNotFoundError(JoplinMCPError):
    """资源未找到"""

    pass
