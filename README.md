# Joplin MCP

基于 FastMCP 的 MCP 服务器，将 Joplin REST API 转换为 MCP 工具，使 LLM 能够直接与 Joplin 笔记应用交互。

## 功能特性

- **无状态设计**：不引入额外数据库，所有数据存储在 Joplin 中
- **API 映射**：将 Joplin REST API 端点映射为 MCP 工具
- **配置驱动**：通过环境变量管理配置

## 安装的包

| 包 | 用途 |
|----|------|
| fastmcp | MCP 框架 |
| httpx | 异步 HTTP 客户端 |
| pydantic | 数据验证 |
| pydantic-settings | 配置管理 |

## 快速开始

### 1. 获取 Joplin Token

1. 打开 Joplin 桌面应用
2. 进入 **工具 → 选项 → Web Clipper**
3. 复制显示的 Token

### 2. 安装依赖

```bash
pip install -e .
```

开发模式（包含测试工具）：

```bash
pip install -e ".[dev]"
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 Joplin Token：

```bash
JOPLIN_MCP_JOPLIN__TOKEN=your_api_token_here
```

### 4. 运行服务器

```bash
fastmcp run src/joplin_mcp/server.py
```

或使用 Python：

```bash
python -m joplin_mcp.server
```

### 5. 配置 MCP 客户端

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "joplin": {
      "command": "fastmcp",
      "args": ["run", "path/to/joplin-mcp/src/joplin_mcp/server.py"],
      "env": {
        "JOPLIN_MCP_JOPLIN__TOKEN": "your_token"
      }
    }
  }
}
```

## 可用的 MCP 工具

### 笔记 (notes)

| 工具 | 描述 |
|------|------|
| `list_notes` | 获取笔记列表 |
| `get_note` | 获取单个笔记详情 |
| `create_note` | 创建新笔记 |
| `update_note` | 更新笔记属性 |
| `delete_note` | 删除笔记 |
| `get_note_tags` | 获取笔记的标签 |
| `get_note_resources` | 获取笔记的附件 |
| `delete_note_revisions` | 删除笔记的修订版本 |

### 笔记本 (folders)

| 工具 | 描述 |
|------|------|
| `list_folders` | 获取笔记本列表（树形结构） |
| `get_folder` | 获取单个笔记本 |
| `create_folder` | 创建新笔记本 |
| `update_folder` | 更新笔记本 |
| `delete_folder` | 删除笔记本 |
| `get_folder_notes` | 获取笔记本内的笔记 |

### 标签 (tags)

| 工具 | 描述 |
|------|------|
| `list_tags` | 获取所有标签 |
| `get_tag` | 获取单个标签详情 |
| `create_tag` | 创建标签 |
| `update_tag` | 更新标签 |
| `delete_tag` | 删除标签 |
| `get_tag_notes` | 获取具有此标签的笔记 |
| `add_tag_to_note` | 为笔记添加标签 |
| `remove_tag_from_note` | 从笔记移除标签 |

### 资源 (resources)

| 工具 | 描述 |
|------|------|
| `list_resources` | 获取资源列表 |
| `get_resource` | 获取资源详情 |
| `get_resource_file` | 下载资源文件 |
| `get_resource_notes` | 获取与资源关联的笔记 |
| `delete_resource` | 删除资源 |

### 搜索 (search)

| 工具 | 描述 |
|------|------|
| `search_notes` | 搜索笔记 |
| `search_folders` | 搜索笔记本 |
| `search_tags` | 搜索标签 |

## 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `JOPLIN_MCP_JOPLIN__TOKEN` | (必填) | Joplin API Token |
| `JOPLIN_MCP_JOPLIN__HOST` | localhost | Joplin 主机 |
| `JOPLIN_MCP_JOPLIN__PORT` | 41184 | Joplin 端口 |
| `JOPLIN_MCP_SERVER_NAME` | Joplin | 服务器名称 |
| `JOPLIN_MCP_DEBUG` | false | 调试模式 |

## 项目结构

```
joplin-mcp/
├── pyproject.toml          # 项目配置
├── .env.example            # 环境变量模板
├── README.md               # 项目说明
├── src/joplin_mcp/
│   ├── server.py           # FastMCP 服务器入口
│   ├── config.py           # 配置管理
│   ├── client.py           # Joplin API 客户端
│   ├── exceptions.py       # 自定义异常
│   └── tools/
│       ├── notes.py        # 笔记工具
│       ├── folders.py      # 笔记本工具
│       ├── tags.py         # 标签工具
│       ├── resources.py    # 资源工具
│       └── search.py       # 搜索工具
└── docs/
    ├── DEV.md              # 设计文档
    └── joplin_api.md       # Joplin API 文档
```

## 开发

安装开发依赖：

```bash
pip install -e ".[dev]"
```

运行测试：

```bash
pytest
```

代码检查：

```bash
ruff check src/
```

## 参考资料

- [Joplin Data API 文档](docs/joplin_api.md)
- [设计文档](docs/DEV.md)
- [FastMCP 文档](https://gofastmcp.com/)
