# Joplin MCP

基于 FastMCP 的 MCP 服务器，将 Joplin REST API 转换为 MCP 工具，使 LLM 能够直接与 Joplin 笔记应用交互。

## 功能特性

- **Task-Centric 设计**：v2 版本采用以任务为中心的设计理念，工具语义清晰，参数精简
- **单一职责**：每个工具只做一件事，工具名称直接表达意图
- **最小参数**：只包含完成该任务必需的参数，减少 LLM 填写负担
- **无状态设计**：不引入额外数据库，所有数据存储在 Joplin 中
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

```bash
# 采用streamable http方式
fastmcp run src/joplin_mcp/server.py --transport http --port 8881
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

## 可用的 MCP 工具 (v2)

### 笔记核心操作 (notes.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `create_note` | `title, body?, folder_id?` | 创建普通笔记 |
| `clip_webpage` | `url, title?, folder_id?` | 剪藏网页 |
| `paste_image_note` | `title, image_data, folder_id?` | 创建带图片的笔记 |
| `get_note` | `note_id, include_body?` | 获取单个笔记详情 |
| `list_notes` | `folder_id?, limit?, sort?, order?` | 获取笔记列表 |
| `list_recent_notes` | `hours?, limit?` | 获取最近更新的笔记 |
| `move_note` | `note_id, folder_id` | 移动笔记到另一个笔记本 |
| `copy_note` | `note_id, folder_id, new_title?` | 复制笔记 |
| `trash_note` | `note_id` | 将笔记移至回收站 |
| `restore_note` | `note_id` | 从回收站恢复笔记 |
| `permanently_delete_note` | `note_id` | 永久删除笔记 |
| `archive_note` | `note_id, archive_folder_id` | 归档笔记 |

### 笔记内容编辑 (notes_content.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `update_note_title` | `note_id, title` | 仅更新标题 |
| `update_note_body` | `note_id, body` | 仅更新正文 |
| `append_to_note` | `note_id, content, as_html?` | 追加内容到末尾 |
| `prepend_to_note` | `note_id, content, as_html?` | 在开头添加内容 |
| `replace_in_note` | `note_id, search, replace` | 替换文本 |

### 待办任务管理 (todos.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `create_todo` | `title, body?, due_date?, folder_id?` | 创建待办事项 |
| `complete_todo` | `note_id` | 标记待办为已完成 |
| `uncomplete_todo` | `note_id` | 取消完成待办 |
| `set_todo_due` | `note_id, due_date` | 设置截止时间 |
| `clear_todo_due` | `note_id` | 清除截止时间 |
| `list_todos` | `status?, folder_id?, limit?` | 获取待办列表 |

### 笔记本管理 (folders.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `list_folders` | `as_tree?` | 获取笔记本列表 |
| `get_folder` | `folder_id` | 获取单个笔记本 |
| `create_folder` | `title, parent_id?` | 创建笔记本 |
| `create_subfolder` | `parent_id, title` | 创建子笔记本 |
| `rename_folder` | `folder_id, title` | 重命名笔记本 |
| `move_folder` | `folder_id, new_parent_id?` | 移动笔记本 |
| `set_folder_icon` | `folder_id, icon` | 设置图标 |
| `get_folder_tree` | `-` | 获取完整树形结构 |
| `get_folder_notes` | `folder_id, limit?, sort?, order?` | 获取笔记本内的笔记 |
| `trash_folder` | `folder_id` | 移至回收站 |
| `restore_folder` | `folder_id` | 从回收站恢复 |
| `permanently_delete_folder` | `folder_id` | 永久删除 |

### 标签管理 (tags.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `list_tags` | `limit?, sort?, order?` | 获取所有标签 |
| `get_tag` | `tag_id` | 获取单个标签 |
| `create_tag` | `title, parent_id?` | 创建标签 |
| `rename_tag` | `tag_id, title` | 重命名标签 |
| `merge_tags` | `source_tag_ids, target_tag_id` | 合并标签 |
| `trash_tag` | `tag_id` | 删除标签 |
| `get_tag_notes` | `tag_id, limit?` | 获取具有某标签的笔记 |
| `add_tag_to_note` | `tag_id, note_id` | 为笔记添加标签 |
| `remove_tag_from_note` | `tag_id, note_id` | 从笔记移除标签 |
| `set_note_tags` | `note_id, tag_ids` | 设置笔记标签（替换） |
| `get_note_tags` | `note_id` | 获取笔记的所有标签 |

### 资源/附件管理 (resources.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `list_resources` | `limit?, sort?, order?` | 获取资源列表 |
| `get_resource` | `resource_id` | 获取资源详情 |
| `get_resource_file` | `resource_id` | 下载资源文件 |
| `get_resource_notes` | `resource_id` | 获取关联的笔记 |
| `delete_resource` | `resource_id, permanent?` | 删除资源 |

### 搜索 (search.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `search_notes` | `query, limit?` | 搜索笔记 |
| `search_folders` | `query, limit?` | 搜索笔记本 |
| `search_tags` | `query, limit?` | 搜索标签 |

### 复合工作流 (workflows.py)

| 工具 | 参数 | 描述 |
|------|------|------|
| `batch_move_notes` | `note_ids, folder_id` | 批量移动笔记 |
| `batch_delete_notes` | `note_ids, permanent?` | 批量删除笔记 |
| `batch_add_tag` | `tag_id, note_ids` | 批量添加标签 |
| `batch_complete_todos` | `note_ids` | 批量完成待办 |
| `inbox_to_folder` | `note_id, target_folder_id` | 整理笔记到文件夹 |
| `process_todo` | `note_id, action` | 处理待办（完成/延期/转笔记） |
| `daily_review` | `date?` | 获取指定日期的笔记回顾 |
| `weekly_review` | `week_start_date?` | 获取本周笔记回顾 |

## 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `JOPLIN_MCP_JOPLIN__TOKEN` | (必填) | Joplin API Token |
| `JOPLIN_MCP_JOPLIN__HOST` | localhost | Joplin 主机 |
| `JOPLIN_MCP_JOPLIN__PORT` | 41184 | Joplin 端口 |
| `JOPLIN_MCP_SERVER_NAME` | Joplin | 服务器名称 |
| `JOPLIN_MCP_DEBUG` | false | 调试模式 |

## 项目结构 (v2)

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
│       ├── __init__.py
│       ├── notes.py        # 笔记核心操作 (12 个工具)
│       ├── notes_content.py # 笔记内容编辑 (5 个工具)
│       ├── folders.py      # 笔记本管理 (12 个工具)
│       ├── tags.py         # 标签管理 (11 个工具)
│       ├── resources.py    # 资源管理 (5 个工具)
│       ├── search.py       # 搜索 (3 个工具)
│       ├── todos.py        # 待办任务 (6 个工具)
│       └── workflows.py    # 复合工作流 (8 个工具)
└── docs/
    ├── v2_design.md        # v2 设计文档
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

## v1 vs v2 对比

| 维度 | v1 | v2 |
|------|----|----|
| 设计思维 | API 映射 | 任务导向 |
| 工具数量 | 17 个 | 62 个 |
| 参数数量 | 多可选参数 | 最小必需参数 |
| 工具命名 | CRUD 风格 | 语义化风格 |
| LLM 负担 | 高（需筛选参数） | 低（参数即意图） |

### 示例对比

**移动笔记到工作笔记本：**

v1:
```python
update_note(note_id="abc123", folder_id="xyz789")
```

v2:
```python
move_note(note_id="abc123", folder_id="xyz789")
```

**标记待办为已完成：**

v1:
```python
update_note(note_id="abc123", todo_completed=1710864000000)
```

v2:
```python
complete_todo(note_id="abc123")  # 自动处理时间戳
```

## 参考资料

- [Joplin Data API 文档](docs/joplin_api.md)
- [v2 设计文档](docs/v2_design.md)
- [FastMCP 文档](https://gofastmcp.com/)
