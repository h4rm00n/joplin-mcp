# Joplin Data API 文档

## 概述

此 API 在 Web Clipper 服务器运行时可用。它通过 REST API 提供对笔记、笔记本、标签和其他 Joplin 对象的访问。即使 Web Clipper 服务器未运行，插件也可以访问此 API。

## 连接方式

要使用 API，首先需要找到服务运行的端口。打开 Joplin 中的 Web Clipper 选项，如果服务正在运行，它会告诉您端口号。通常运行在端口 **41184** 上。

### 查找端口的算法示例

```javascript
let port = null;
for (let portToTest = 41184; portToTest <= 41194; portToTest++) {
    const result = pingPort(portToTest); // 调用 GET /ping
    if (result == 'JoplinClipperServer') {
        port = portToTest; // 找到端口
        break;
    }
}
```

## 授权 (Authorisation)

为了防止未经授权的应用程序访问 API，调用必须进行身份验证。为此，您必须为每个 API 调用提供令牌（token）作为查询参数。您可以从 Joplin 桌面应用程序的 Web Clipper 选项屏幕获取此令牌。

### cURL 调用示例

```bash
curl http://localhost:41184/notes?token=ABCD123ABCD123ABCD123ABCD123ABCD123
```

在下面的文档中，令牌将不会每次都指定，但您需要包含它。

如果需要，您还可以[以编程方式请求令牌](/help/dev/spec/clipper_auth)。

## 使用 API

所有调用（除非另有说明）都接收和发送 **JSON 数据**。

### 创建新笔记示例

```bash
curl --data '{ "title": "My note", "body": "Some note in **Markdown**"}' http://localhost:41184/notes
```

### URL 参数说明

在下面的文档中，调用可能包含特殊参数（如 `:id` 或 `:note_id`）。您需要用实际的项目 ID 或笔记 ID 替换这些参数。

例如，对于端点 `DELETE /tags/:id/notes/:note_id`，要从 ID 为 "EFGH789" 的笔记中移除 ID 为 "ABCD1234" 的标签，您可以运行：

```bash
curl -X DELETE http://localhost:41184/tags/ABCD1234/notes/EFGH789
```

### HTTP 动词说明

API 支持的四种动词如下：

| 动词 | 说明 |
|------|------|
| **GET** | 用于检索项目（笔记、笔记本等） |
| **POST** | 用于创建新项目。通常大多数项目属性是可选的。如果省略任何属性，将使用默认值 |
| **PUT** | 用于更新项目。在传统 REST API 中，PUT 用于完全替换项目，但在此 API 中，它只会替换提供的属性。例如，如果您 PUT `{"title": "my new title"}`，只有 "title" 属性会被更改，其他属性将保持不变 |
| **DELETE** | 用于删除项目 |

## 过滤数据 (Filtering data)

您可以使用 `fields=` 查询参数更改 API 返回的字段，该参数接受逗号分隔的字段列表。

### 示例

获取笔记的经度和纬度：

```bash
curl http://localhost:41184/notes/ABCD123?fields=longitude,latitude
```

获取所有标签的 ID：

```bash
curl http://localhost:41184/tags?fields=id
```

**默认情况下**，API 结果将包含以下字段：**id**、**parent_id**、**title**

## 分页 (Pagination)

所有返回多个结果的 API 调用都将被分页，并返回以下结构：

| 键 | 是否始终存在 | 描述 |
|-----|-------------|------|
| `items` | 是 | 您请求的项目数组 |
| `has_more` | 是 | 如果为 `true`，表示此页之后还有更多项目。如果为 `false`，表示您已到达数据集的末尾 |

您可以使用 `order_by` 和 `order_dir` 查询参数指定结果的排序方式，使用 `page` 参数指定检索哪一页（从 1 开始，默认为 1）。您可以使用 `limit` 参数指定要返回的项目数（最大为 100 个项目）。

### 分页示例

以下调用将发起请求以获取所有笔记，每次 10 个，按 "updated_time" 升序排序：

```bash
curl http://localhost:41184/notes?order_by=updated_time&order_dir=ASC&limit=10
```

返回结果示例：

```json
{ "items": [ /* 10 条笔记 */ ], "has_more": true }
```

然后您可以使用以下查询继续获取结果：

```bash
curl http://localhost:41184/notes?order_by=updated_time&order_dir=ASC&limit=10&page=2
```

最终您将获得不包含 "has_more" 参数的结果，此时您已检索完所有结果。

### 获取所有笔记的伪代码示例

```javascript
async function fetchJson(url) {
    return (await fetch(url)).json();
}

async function fetchAllNotes() {
    let pageNum = 1;
    do {
        const response = await fetchJson(`http://localhost:41184/notes?page=${pageNum++}`);
        console.info('Printing notes:', response.items);
    } while (response.has_more)
}
```

## 错误处理 (Error handling)

在出现错误的情况下，将返回 HTTP 状态码 >= 400，以及一个提供有关错误的更多信息的 JSON 对象。JSON 对象的格式为 `{ "error": "description of error" }`。

## 关于属性类型

- 文本为 UTF-8 编码
- 所有日期/时间为毫秒级的 Unix 时间戳
- 布尔值为整数值 0 或 1

## 测试服务是否可用

调用 **GET /ping** 检查服务是否可用。如果正常工作，应返回 "JoplinClipperServer"。

## 搜索 (Searching)

调用 **GET /search?query=YOUR_QUERY** 搜索笔记。此端点支持使用 `field` 参数（建议使用该参数，以便只获取所需数据）。查询语法如主文档中所述：[https://joplinapp.org/help/apps/search](https://joplinapp.org/help/apps/search)

要检索非笔记项目（如笔记本或标签），请添加 `type` 参数并将其设置为所需的[项目类型名称](#item-type-ids)。在这种情况下，将不使用全文搜索，而是进行简单的大小写不敏感搜索。您还可以使用 `*` 作为通配符。这对于按标题检索笔记本或标签非常方便。

### 搜索示例

获取名为 `recipes` 的笔记本：

```
GET /search?query=recipes&type=folder
```

获取所有以 `project-` 开头的标签：

```
GET /search?query=project-*&type=tag
```

## 项目类型 ID (Item type IDs)

某些从 API 检索的对象可能会引用项目类型 ID。以下是名称和 ID 之间的对应关系：

| 名称 | 值 |
|------|-----|
| note | 1 |
| folder | 2 |
| setting | 3 |
| resource | 4 |
| tag | 5 |
| note_tag | 6 |
| search | 7 |
| alarm | 8 |
| master_key | 9 |
| item_change | 10 |
| note_resource | 11 |
| resource_local_state | 12 |
| revision | 13 |
| migration | 14 |
| smart_filter | 15 |
| command | 16 |

---

## Notes（笔记）

### 属性 (Properties)

| 名称 | 类型 | 描述 |
|------|------|------|
| id | text | |
| parent_id | text | 包含此笔记的笔记本的 ID。更改此 ID 可将笔记移动到其他笔记本 |
| title | text | 笔记标题 |
| body | text | Markdown 格式的笔记正文。也可能包含 HTML |
| created_time | int | 笔记创建时间 |
| updated_time | int | 笔记最后更新时间 |
| is_conflict | int | 表示笔记是否为冲突笔记 |
| latitude | numeric | 纬度 |
| longitude | numeric | 经度 |
| altitude | numeric | 海拔 |
| author | text | 作者 |
| source_url | text | 笔记来源的完整 URL |
| is_todo | int | 表示此笔记是否为待办事项 |
| todo_due | int | 待办事项到期时间。届时将触发警报 |
| todo_completed | int | 表示待办事项是否已完成。这是毫秒级时间戳 |
| source | text | |
| source_application | text | |
| application_data | text | |
| order | numeric | |
| user_created_time | int | 笔记创建时间。可能与 created_time 不同，因为可以由用户手动设置 |
| user_updated_time | int | 笔记最后更新时间。可能与 updated_time 不同，因为可以由用户手动设置 |
| encryption_cipher_text | text | |
| encryption_applied | int | |
| markup_language | int | |
| is_shared | int | 笔记是否已发布 |
| share_id | text | 包含笔记的 Joplin Server/Cloud 共享的 ID。如果未共享则为空 |
| conflict_original_id | text | |
| master_key_id | text | |
| user_data | text | |
| deleted_time | int | |
| body_html | text | HTML 格式的笔记正文 |
| base_url | text | 如果提供了 `body_html` 并且包含相对 URL，请提供 `base_url` 参数，以便将所有 URL 转换为绝对 URL。基本 URL 基本上是获取 HTML 的位置，减去查询（"?" 之后的所有内容）。例如，如果原始页面是 `https://stackoverflow.com/search?q=%5Bjava%5D+test`，则基本 URL 是 `https://stackoverflow.com/search` |
| image_data_url | text | 要附加到笔记的图像，采用 [Data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs) 格式 |
| crop_rect | text | 如果提供了图像，您还可以指定一个可选的矩形用于裁剪图像。格式为 `{ x: x, y: y, width: width, height: height }` |

### API 端点

#### GET /notes

获取所有笔记

默认情况下，此调用将返回所有笔记，**除了**回收站中的笔记和任何冲突笔记。要包含这些，您可以指定 `include_deleted=1` 和 `include_conflicts=1` 作为查询参数。

#### GET /notes/:id

获取 ID 为 :id 的笔记

#### GET /notes/:id/tags

获取附加到此笔记的所有标签

#### GET /notes/:id/resources

获取附加到此笔记的所有资源

#### POST /notes

创建新笔记

您可以将笔记正文指定为 Markdown（通过设置 `body` 参数），或 HTML（通过设置 `body_html`）。

**示例：**

创建 Markdown 格式的笔记：

```bash
curl --data '{ "title": "My note", "body": "Some note in **Markdown**"}' http://127.0.0.1:41184/notes
```

创建 HTML 格式的笔记：

```bash
curl --data '{ "title": "My note", "body_html": "Some note in <b>HTML</b>"}' http://127.0.0.1:41184/notes
```

创建笔记并附加图像：

```bash
curl --data '{ "title": "Image test", "body": "Here is Joplin icon:", "image_data_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAANZJREFUeNoAyAA3/wFwtO3K6gUB/vz2+Prw9fj/+/r+/wBZKAAExOgF4/MC9ff+MRH6Ui4E+/0Bqc/zutj6AgT+/Pz7+vv7++nu82c4DlMqCvLs8goA/gL8/fz09fb59vXa6vzZ6vjT5fbn6voD/fwC8vX4UiT9Zi//APHyAP8ACgUBAPv5APz7BPj2+DIaC2o3E+3o6ywaC5fT6gD6/QD9/QEVf9kD+/dcLQgJA/7v8vqfwOf18wA1IAIEVycAyt//v9XvAPv7APz8LhoIAPz9Ri4OAgwARgx4W/6fVeEAAAAASUVORK5CYII="}' http://127.0.0.1:41184/notes
```

##### 创建具有特定 ID 的笔记

创建新笔记时，系统会自动为其分配一个新的唯一 ID，因此**通常您不需要设置 ID**。但是，如果出于某种原因您想设置它，可以将其作为 `id` 属性提供。它需要是一个 **32 个字符长的十六进制字符串**。**确保它是唯一的**，例如通过使用编程语言中可用的任何 GUID 函数生成它。

```bash
curl --data '{ "id": "00a87474082744c1a8515da6aa5792d2", "title": "My note with custom ID"}' http://127.0.0.1:41184/notes
```

#### PUT /notes/:id

设置 ID 为 :id 的笔记的属性

#### DELETE /notes/:id

删除 ID 为 :id 的笔记

默认情况下，笔记将被**移至回收站**。要永久删除它，请添加查询参数 `permanent=1`

#### DELETE /notes/:id/revisions

删除附加到此笔记的所有修订版本

---

## Folders（文件夹/笔记本）

这实际上是笔记本。在内部，笔记本被称为 "folders"。

### 属性 (Properties)

| 名称 | 类型 | 描述 |
|------|------|------|
| id | text | |
| title | text | 文件夹标题 |
| created_time | int | 文件夹创建时间 |
| updated_time | int | 文件夹最后更新时间 |
| user_created_time | int | 文件夹创建时间。可能与 created_time 不同，因为可以由用户手动设置 |
| user_updated_time | int | 文件夹最后更新时间。可能与 updated_time 不同，因为可以由用户手动设置 |
| encryption_cipher_text | text | |
| encryption_applied | int | |
| parent_id | text | |
| is_shared | int | |
| share_id | text | 包含文件夹的 Joplin Server/Cloud 共享的 ID。如果未共享则为空 |
| master_key_id | text | |
| icon | text | |
| user_data | text | |
| deleted_time | int | |

### API 端点

#### GET /folders

获取所有文件夹

文件夹作为树形结构返回。笔记本的子笔记本（如果有）位于 `children` 键下。

#### GET /folders/:id

获取 ID 为 :id 的文件夹

#### GET /folders/:id/notes

获取此文件夹内的所有笔记

#### POST /folders

创建新文件夹

#### PUT /folders/:id

设置 ID 为 :id 的文件夹的属性

#### DELETE /folders/:id

删除 ID 为 :id 的文件夹

默认情况下，文件夹将被**移至回收站**。要永久删除它，请添加查询参数 `permanent=1`

---

## Resources（资源）

### 属性 (Properties)

| 名称 | 类型 | 描述 |
|------|------|------|
| id | text | |
| title | text | 资源标题 |
| mime | text | MIME 类型 |
| filename | text | 文件名 |
| created_time | int | 资源创建时间 |
| updated_time | int | 资源最后更新时间 |
| user_created_time | int | 资源创建时间。可能与 created_time 不同，因为可以由用户手动设置 |
| user_updated_time | int | 资源最后更新时间。可能与 updated_time 不同，因为可以由用户手动设置 |
| file_extension | text | 文件扩展名 |
| encryption_cipher_text | text | |
| encryption_applied | int | |
| encryption_blob_encrypted | int | |
| size | int | 文件大小 |
| is_shared | int | |
| share_id | text | 包含资源的 Joplin Server/Cloud 共享的 ID。如果未共享则为空 |
| master_key_id | text | |
| user_data | text | |
| blob_updated_time | int | |
| ocr_text | text | |
| ocr_details | text | |
| ocr_status | int | |
| ocr_error | text | |
| ocr_driver_id | int | |

### API 端点

#### GET /resources

获取所有资源

#### GET /resources/:id

获取 ID 为 :id 的资源

#### GET /resources/:id/file

获取与此资源关联的实际文件

#### GET /resources/:id/notes

获取与资源关联的笔记（ID）

#### POST /resources

创建新资源

创建新资源很特殊，因为您还需要上传文件。与其他 API 调用不同，此调用必须使用 "multipart/form-data" Content-Type。文件数据必须传递到 "data" 表单字段，其他属性传递到 "props" 表单字段。

**cURL 示例：**

```bash
curl -F 'data=@/path/to/file.jpg' -F 'props={"title":"my resource title"}' http://localhost:41184/resources
```

要**更新**资源内容，您可以使用相同的参数进行 PUT 请求：

```bash
curl -X PUT -F 'data=@/path/to/file.jpg' -F 'props={"title":"my modified title"}' http://localhost:41184/resources/8fe1417d7b184324bf6b0122b76c4696
```

"data" 字段是必需的，而 "props" 不是。如果未指定，将使用默认值。

如果您只需要更新资源属性（标题等）而不更改内容，可以进行常规的 PUT 请求：

```bash
curl -X PUT --data '{"title": "My new title"}' http://localhost:41184/resources/8fe1417d7b184324bf6b0122b76c4696
```

**从插件创建资源的语法也略有不同：**

```javascript
await joplin.data.post(
    ["resources"],
    null,
    { title: "test.jpg" }, // 资源元数据
    [
        {
            path: "/path/to/test.jpg", // 实际文件
        },
    ]
);
```

#### PUT /resources/:id

设置 ID 为 :id 的资源的属性

您也可以更新文件数据（参见 `POST /resources` 示例）。

#### DELETE /resources/:id

删除 ID 为 :id 的资源

---

## Tags（标签）

### 属性 (Properties)

| 名称 | 类型 | 描述 |
|------|------|------|
| id | text | |
| title | text | 标签标题 |
| created_time | int | 标签创建时间 |
| updated_time | int | 标签最后更新时间 |
| user_created_time | int | 标签创建时间。可能与 created_time 不同，因为可以由用户手动设置 |
| user_updated_time | int | 标签最后更新时间。可能与 updated_time 不同，因为可以由用户手动设置 |
| encryption_cipher_text | text | |
| encryption_applied | int | |
| is_shared | int | |
| parent_id | text | |
| user_data | text | |

### API 端点

#### GET /tags

获取所有标签

#### GET /tags/:id

获取 ID 为 :id 的标签

#### GET /tags/:id/notes

获取具有此标签的所有笔记

#### POST /tags

创建新标签

#### POST /tags/:id/notes

将笔记发布到此端点以将标签添加到笔记。笔记数据必须至少包含一个 ID 属性（所有其他属性将被忽略）。

#### PUT /tags/:id

设置 ID 为 :id 的标签的属性

#### DELETE /tags/:id

删除 ID 为 :id 的标签

#### DELETE /tags/:id/notes/:note_id

从笔记中移除标签

---

## Revisions（修订版本）

### 属性 (Properties)

| 名称 | 类型 | 描述 |
|------|------|------|
| id | text | |
| parent_id | text | |
| item_type | int | |
| item_id | text | |
| item_updated_time | int | |
| title_diff | text | |
| body_diff | text | |
| metadata_diff | text | |
| encryption_cipher_text | text | |
| encryption_applied | int | |
| updated_time | int | |
| created_time | int | |

### API 端点

#### GET /revisions

获取所有修订版本

#### GET /revisions/:id

获取 ID 为 :id 的修订版本

#### POST /revisions

创建新修订版本

#### PUT /revisions/:id

设置 ID 为 :id 的修订版本的属性

#### DELETE /revisions/:id

删除 ID 为 :id 的修订版本

---

## Events（事件）

此端点可用于检索最新的笔记更改。目前仅跟踪笔记更改。

### 属性 (Properties)

| 名称 | 类型 | 描述 |
|------|------|------|
| id | int | |
| item_type | int | 项目类型（参见上表获取项目类型列表） |
| item_id | text | 项目 ID |
| type | int | 更改类型 - 1（创建）、2（更新）或 3（删除） |
| created_time | int | 事件生成时间 |
| source | int | 未使用 |
| before_change_item | text | 未使用 |

### API 端点

#### GET /events

返回最近事件的分页列表。应提供 `cursor` 属性，该属性告诉应从什么时间点检索事件。API 将返回 `cursor` 属性（告诉从何处恢复检索事件），以及 `has_more`（告诉是否可以检索更多更改）和 `items` 属性（将包含事件列表）。事件保留最多 90 天。

如果未提供 `cursor` 属性，API 将返回最新的更改 ID。这可用于以后检索未来事件。

结果是分页的，因此您可能需要多次调用才能检索所有事件。使用 `has_more` 属性了解是否可以检索更多事件。

#### GET /events/:id

返回具有给定 ID 的事件
