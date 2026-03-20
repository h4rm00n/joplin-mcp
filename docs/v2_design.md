# Joplin MCP v2 设计文档 - Task-Centric 架构

## 1. 概述

### 1.1 设计目标

v2 版本从 **API-Centric**（以 API 为中心）转向 **Task-Centric**（以任务为中心）的设计理念，将通用的 CRUD 操作拆分为具体的业务操作，减少 LLM 需要填写的参数数量，提高工具使用的准确性和效率。

### 1.2 问题背景

在 v1 版本中，每个 MCP 工具都直接映射 Joplin OpenAPI 的参数，导致 LLM 需要填写大量冗余参数。以 `update_note()` 为例：

```python
# v1 - 8 个可选参数，但典型使用场景只需 2 个
async def update_note(
    note_id: str,
    title: str | None = None,
    body: str | None = None,
    body_html: str | None = None,
    is_todo: bool | None = None,
    todo_due: int | None = None,
    todo_completed: int | None = None,
    folder_id: str | None = None,
) -> dict:
```

**问题表现：**
- 参数数量过多，认知负担重
- Token 浪费，工具 schema 包含大量无用描述
- 易出错，参数越多填错概率越大

### 1.3 设计原则

1. **单一职责**：每个工具只做一件事
2. **最小参数**：只包含完成该任务必需的参数
3. **语义清晰**：工具名称直接表达意图
4. **组合使用**：复杂操作由多个简单工具组合完成

---

## 2. Notes（笔记）任务设计

### 2.1 笔记创建类任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `create_note` | `title, body, folder_id?` | 创建普通笔记 | POST /notes |
| `create_todo` | `title, body?, due_date?, folder_id?` | 创建待办事项 | POST /notes (is_todo=1) |
| `clip_webpage` | `url, title?, folder_id?` | 剪藏网页 | POST /notes (带 source_url) |
| `paste_image_note` | `title, image_data, folder_id?` | 创建带图片的笔记 | POST /notes (带 image_data_url) |

### 2.2 笔记内容编辑任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `update_note_title` | `note_id, title` | 仅更新标题 | PUT /notes/:id |
| `update_note_body` | `note_id, body` | 仅更新正文 | PUT /notes/:id |
| `append_to_note` | `note_id, content, as_html?` | 追加内容到笔记末尾 | GET + PUT /notes/:id |
| `prepend_to_note` | `note_id, content, as_html?` | 在笔记开头添加内容 | GET + PUT /notes/:id |
| `replace_in_note` | `note_id, search, replace` | 替换笔记中的文本 | GET + PUT /notes/:id |

### 2.3 笔记组织任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `move_note` | `note_id, folder_id` | 移动笔记到另一个笔记本 | PUT /notes/:id (parent_id) |
| `copy_note` | `note_id, folder_id, new_title?` | 复制笔记到另一个笔记本 | GET + POST /notes |
| `archive_note` | `note_id` | 归档笔记（移动到归档笔记本） | 配置驱动的移动 |
| `trash_note` | `note_id` | 将笔记移至回收站 | DELETE /notes/:id |
| `restore_note` | `note_id` | 从回收站恢复笔记 | PUT /notes/:id (deleted_time=0) |
| `permanently_delete_note` | `note_id` | 永久删除笔记 | DELETE /notes/:id?permanent=1 |

### 2.4 待办任务管理

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `complete_todo` | `note_id` | 标记待办为已完成 | PUT /notes/:id (todo_completed=now) |
| `uncomplete_todo` | `note_id` | 取消完成待办 | PUT /notes/:id (todo_completed=0) |
| `set_todo_due` | `note_id, due_date` | 设置待办截止时间 | PUT /notes/:id (todo_due) |
| `clear_todo_due` | `note_id` | 清除待办截止时间 | PUT /notes/:id (todo_due=0) |

### 2.5 笔记查询任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `get_note` | `note_id, include_body?` | 获取单个笔记详情 | GET /notes/:id |
| `list_notes` | `folder_id?, limit?, sort?` | 获取笔记列表 | GET /notes |
| `list_todos` | `status?, folder_id?, limit?` | 获取待办列表（可过滤完成状态） | GET /notes?is_todo=1 |
| `list_recent_notes` | `hours?, limit?` | 获取最近更新的笔记 | GET /notes?order_by=updated_time |
| `search_notes` | `query, limit?` | 搜索笔记 | GET /search?query=... |

---

## 3. Folders（笔记本）任务设计

### 3.1 笔记本创建与组织

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `create_folder` | `title, parent_id?` | 创建笔记本（可指定父笔记本） | POST /folders |
| `create_subfolder` | `parent_id, title` | 创建子笔记本 | POST /folders (parent_id) |
| `move_folder` | `folder_id, new_parent_id?` | 移动笔记本（new_parent_id=null 表示移到根目录） | PUT /folders/:id |
| `rename_folder` | `folder_id, title` | 重命名笔记本 | PUT /folders/:id |
| `set_folder_icon` | `folder_id, icon` | 设置笔记本图标 emoji | PUT /folders/:id |

### 3.2 笔记本删除任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `trash_folder` | `folder_id` | 将笔记本移至回收站 | DELETE /folders/:id |
| `restore_folder` | `folder_id` | 从回收站恢复笔记本 | PUT /folders/:id (deleted_time=0) |
| `permanently_delete_folder` | `folder_id` | 永久删除笔记本 | DELETE /folders/:id?permanent=1 |

### 3.3 笔记本查询任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `list_folders` | `as_tree?` | 获取笔记本列表（可选树形结构） | GET /folders |
| `get_folder` | `folder_id` | 获取单个笔记本详情 | GET /folders/:id |
| `get_folder_notes` | `folder_id, limit?, sort?` | 获取笔记本内的笔记 | GET /folders/:id/notes |
| `get_folder_tree` | - | 获取完整的笔记本树形结构 | GET /folders |
| `search_folder` | `query` | 按名称搜索笔记本 | GET /search?type=folder |

---

## 4. Tags（标签）任务设计

### 4.1 标签管理任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `create_tag` | `title, parent_id?` | 创建标签（可创建层级标签） | POST /tags |
| `rename_tag` | `tag_id, title` | 重命名标签 | PUT /tags/:id |
| `merge_tags` | `source_tag_ids, target_tag_id` | 合并多个标签到一个 | 批量操作 |
| `trash_tag` | `tag_id` | 删除标签 | DELETE /tags/:id |
| `list_tags` | `limit?, sort?` | 获取所有标签 | GET /tags |
| `search_tag` | `query` | 搜索标签 | GET /search?type=tag |

### 4.2 标签与笔记关联任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `add_tag_to_note` | `tag_id, note_id` | 为笔记添加标签 | POST /tags/:id/notes |
| `remove_tag_from_note` | `tag_id, note_id` | 从笔记移除标签 | DELETE /tags/:id/notes/:note_id |
| `set_note_tags` | `note_id, tag_ids` | 设置笔记的标签（替换现有） | 批量操作 |
| `get_note_tags` | `note_id` | 获取笔记的所有标签 | GET /notes/:id/tags |
| `get_tag_notes` | `tag_id, limit?` | 获取具有某标签的所有笔记 | GET /tags/:id/notes |

---

## 5. Resources（资源/附件）任务设计

### 5.1 资源管理任务

| 工具名 | 参数 | 描述 | 对应 API |
|--------|------|------|---------|
| `upload_resource` | `file_data, title?, note_id?` | 上传附件（可关联到笔记） | POST /resources |
| `attach_to_note` | `resource_id, note_id` | 将资源关联到笔记 | POST /resources/:id/notes |
| `get_resource` | `resource_id` | 获取资源详情 | GET /resources/:id |
| `download_resource` | `resource_id` | 下载资源文件 | GET /resources/:id/file |
| `list_resources` | `limit?, note_id?` | 获取资源列表 | GET /resources |
| `delete_resource` | `resource_id` | 删除资源 | DELETE /resources/:id |

---

## 6. 跨对象复合任务

### 6.1 批量操作

| 工具名 | 参数 | 描述 |
|--------|------|------|
| `batch_move_notes` | `note_ids, folder_id` | 批量移动笔记 |
| `batch_delete_notes` | `note_ids, permanent?` | 批量删除笔记 |
| `batch_add_tag` | `tag_id, note_ids` | 批量为笔记添加标签 |
| `batch_complete_todos` | `note_ids` | 批量完成待办 |

### 6.2 工作流任务

| 工具名 | 参数 | 描述 |
|--------|------|------|
| `inbox_to_folder` | `note_id, target_folder_id` | 将笔记从收件箱整理到目标文件夹 |
| `process_todo` | `note_id, action` | 处理待办（完成/延期/转笔记） |
| `daily_review` | `date?` | 获取指定日期的笔记回顾 |
| `weekly_review` | `week_start_date?` | 获取本周笔记回顾 |

---

## 7. 工具命名规范

### 7.1 基础格式

```
<action>_<object>          # 基础格式
  ├── create_note          # 创建 + 对象
  ├── move_note            # 动作 + 对象
  ├── complete_todo        # 动作 + 对象
  └── add_tag_to_note      # 动作 + 源对象 + 目标对象
```

### 7.2 动作词汇表

| 动作 | 含义 |
|------|------|
| `create` | 创建新对象 |
| `get` | 获取单个对象详情 |
| `list` | 获取对象列表 |
| `update` | 更新对象属性（通用） |
| `rename` | 重命名 |
| `move` | 移动位置 |
| `copy` | 复制 |
| `delete` | 删除 |
| `trash` | 移至回收站 |
| `restore` | 从回收站恢复 |
| `add_X_to_Y` | 将 X 关联到 Y |
| `remove_X_from_Y` | 从 Y 移除 X |
| `set_X` | 设置 X 属性 |
| `clear_X` | 清除 X 属性 |
| `search` | 搜索 |
| `append` | 追加内容 |
| `prepend` | 在开头添加 |

---

## 8. 参数设计原则

### 8.1 参数类型

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 必需参数 | 无后缀 | `note_id: str` |
| 可选参数 | `?` 后缀 | `folder_id: str \| None = None` |
| 布尔参数 | 明确语义 | `permanent: bool = False` |
| 枚举参数 | 字面量联合 | `sort: Literal["created", "updated", "title"] = "updated"` |

### 8.2 参数默认值

```python
# 分页参数
limit: int = 10           # 合理默认值
page: int = 1

# 排序参数
sort: str = "updated"     # 最常用的排序
order: Literal["asc", "desc"] = "desc"

# 可选过滤
folder_id: str | None = None  # None 表示不过滤
```

---

## 9. 模块组织

```
src/joplin_mcp/tools/
├── __init__.py
├── notes.py          # 笔记核心操作
├── notes_content.py  # 笔记内容编辑（append, replace 等）
├── todos.py          # 待办专用操作
├── folders.py        # 笔记本操作
├── tags.py           # 标签操作
├── resources.py      # 资源/附件操作
├── search.py         # 搜索操作
└── workflows.py      # 复合工作流
```

---

## 10. 示例对比：v1 vs v2

### 场景 1：移动笔记到工作笔记本

**v1 方式：**
```python
# LLM 需要调用 update_note，从 8 个参数中选择
update_note(
    note_id="abc123",      # 必需
    folder_id="xyz789",    # 必需
    # 其他 6 个参数需要明确为 None 或忽略
)
```

**v2 方式：**
```python
# LLM 直接调用语义明确的工具
move_note(
    note_id="abc123",
    folder_id="xyz789"
)
```

### 场景 2：标记待办为已完成

**v1 方式：**
```python
update_note(
    note_id="abc123",
    todo_completed=1710864000000,  # 需要计算当前时间戳
    # 其他参数忽略
)
```

**v2 方式：**
```python
complete_todo(note_id="abc123")  # 工具内部自动处理时间戳
```

---

## 11. 实现建议

### 11.1 工具注册模式

```python
from fastmcp import FastMCP
from ..client import JoplinClient
from ..config import Settings

def register_tools(mcp: FastMCP, settings: Settings):
    client = JoplinClient(settings.joplin.base_url, settings.joplin.token)
    
    @mcp.tool(description="移动笔记到指定笔记本")
    async def move_note(note_id: str, folder_id: str) -> dict:
        return await client.put(f"/notes/{note_id}", {"parent_id": folder_id})
    
    @mcp.tool(description="标记待办为已完成")
    async def complete_todo(note_id: str) -> dict:
        import time
        return await client.put(f"/notes/{note_id}", {
            "todo_completed": int(time.time() * 1000)
        })
```

### 11.2 工具描述优化

```python
@mcp.tool(description="""
移动笔记到另一个笔记本。

使用场景：
- 整理笔记到合适的分类
- 将临时笔记归档

参数：
- note_id: 要移动的笔记 ID
- folder_id: 目标笔记本 ID（可通过 list_folders 获取）
""")
async def move_note(note_id: str, folder_id: str) -> dict:
    ...
```

---

## 12. 总结

v2 设计的核心转变：

| 维度 | v1 | v2 |
|------|----|----|
| 设计思维 | API 映射 | 任务导向 |
| 工具数量 | 少而通用 | 多而具体 |
| 参数数量 | 多可选参数 | 最小必需参数 |
| 工具命名 | CRUD 风格 | 语义化风格 |
| LLM 负担 | 高（需筛选参数） | 低（参数即意图） |
| 可扩展性 | 低 | 高（可按需添加） |
