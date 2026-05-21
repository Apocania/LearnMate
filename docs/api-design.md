# API Design

本文档用于记录前后端接口设计。

当前接口统一使用 `/api` 前缀。

## Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | 游客 | 注册并返回 token。用户名会去空格、小写化，只允许英文、数字和下划线，长度 3-32 位。 |
| POST | `/api/auth/login` | 游客 | 登录并返回 token 和用户信息。 |

## Users

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/users/me` | 登录用户 | 返回当前用户信息。 |
| POST | `/api/users/me/avatar` | 登录用户 | 上传个人头像，支持 JPG、PNG、WebP、GIF，返回更新后的用户信息。 |

角色：

```text
student  学生
mentor   伴学师
```

## Courses

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/courses` | 可选 | 课程列表。游客可访问；登录学生会额外返回本人是否已加入。 |
| POST | `/api/courses` | 伴学师 | 创建课程。 |
| GET | `/api/courses/{course_id}` | 可选 | 课程详情。 |
| PUT | `/api/courses/{course_id}` | 伴学师本人 | 编辑自己创建的课程。 |
| DELETE | `/api/courses/{course_id}` | 伴学师本人 | 删除自己创建的课程，返回 `204`。 |
| POST | `/api/courses/{course_id}/enroll` | 学生 | 加入课程。重复加入会保持幂等。 |
| DELETE | `/api/courses/{course_id}/enroll` | 学生 | 退出课程。未加入时保持幂等。 |
| GET | `/api/courses/{course_id}/chapters` | 游客 | 查看课程章节目录。 |
| POST | `/api/courses/{course_id}/chapters` | 伴学师本人 | 创建课程章节。 |
| PUT | `/api/courses/{course_id}/chapters/{chapter_id}` | 伴学师本人 | 编辑课程章节。 |
| DELETE | `/api/courses/{course_id}/chapters/{chapter_id}` | 伴学师本人 | 删除课程章节，返回 `204`。 |

课程响应字段：

```text
id
title
description
teacher_id
teacher_name
status
enrollment_count
joined_by_me
```

## Forum

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/forum/posts` | 可选 | 帖子分页列表，游客可浏览。支持 `course_id`、`keyword`、`page`、`page_size`，伴学师可额外使用 `status_filter`。 |
| POST | `/api/forum/posts` | 学生/伴学师 | 发布帖子，使用 `multipart/form-data`，字段包含 `title`、`content`、可选 `course_id` 和最多 5 个 `attachments`。正文按 Markdown 文本保存，前端负责预览和展示渲染。 |
| GET | `/api/forum/attachments/{stored_name}/download` | 游客 | 下载帖子附件。 |
| GET | `/api/forum/posts/{post_id}/comments` | 游客 | 查看评论。 |
| POST | `/api/forum/posts/{post_id}/comments` | 学生/伴学师 | 发布评论。 |
| DELETE | `/api/forum/comments/{comment_id}` | 评论作者/伴学师 | 删除评论，返回 `204`。 |
| POST | `/api/forum/posts/{post_id}/like` | 学生/伴学师 | 切换点赞状态。 |
| DELETE | `/api/forum/posts/{post_id}` | 伴学师 | 删除帖子，返回 `204`。 |
| PATCH | `/api/forum/posts/{post_id}/status` | 伴学师 | 隐藏或恢复帖子，`status` 支持 `active` / `hidden`。 |

帖子列表响应为分页对象，包含 `items`、`total`、`page`、`page_size`。帖子响应包含 `like_count`、`comment_count`、`liked_by_me`、`author_avatar_url`、`attachments`、`course_title` 和 `status`；评论响应包含 `author_avatar_url` 和 `can_delete`。点赞和评论会给帖子作者生成消息提醒，自己操作自己的帖子不会提醒自己。论坛附件当前使用后端本地 `storage/forum-attachments` 保存，下载接口会校验文件名避免路径穿越。

## Messages

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/messages` | 登录用户 | 当前用户消息列表。 |
| GET | `/api/messages/unread-count` | 登录用户 | 当前用户未读消息数。 |
| POST | `/api/messages/{message_id}/read` | 消息接收者 | 标记单条消息已读。 |
| POST | `/api/messages/read-all` | 登录用户 | 全部标记已读，返回 `204`。 |
| GET | `/api/messages/student-recipients` | 伴学师 | 获取可接收私信的学生列表。 |
| POST | `/api/messages/private` | 伴学师 | 给指定学生发送私信。 |
| POST | `/api/messages/announcements` | 伴学师 | 给所有学生发送公告。 |

消息类型：

```text
like          点赞提醒
comment       评论提醒
private       私信
announcement  公告
```

## Files

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/files` | 游客 | 课件列表，支持 `course_id` 和 `chapter_id` 筛选。 |
| POST | `/api/files/upload` | 伴学师 | 上传课件。使用 `multipart/form-data`，支持可选 `course_id` 和 `chapter_id`，限制大小和 MIME 类型。 |
| GET | `/api/files/{file_id}/download` | 游客 | 浏览或下载课件。 |
| DELETE | `/api/files/{file_id}` | 上传者本人且为伴学师 | 删除自己上传的课件，返回 `204`。 |

当前默认上传限制：

```text
最大大小：20MB
允许类型：PDF、PNG、JPEG、TXT、DOCX
```

上传文本、Markdown、DOCX 和安装 `pypdf` 后的 PDF 会自动抽取文本、切分为知识库 chunk，用于 AI 伴学检索。`STORAGE_BACKEND=local` 使用本地目录；`STORAGE_BACKEND=minio` 使用 MinIO。

## Assistant

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/assistant/messages` | 学生/伴学师 | 发送 AI 伴学问题，返回回答和引用列表。 |

请求字段：

```text
content
course_id 可选
session_id 可选
```

响应字段：

```text
session_id
answer
citations[].document_id
citations[].title
citations[].chunk_index
citations[].snippet
citations[].source_url
```

后端会按问题检索知识库 chunk。配置 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL` 后调用 OpenAI 兼容大模型；未配置时使用本地检索式回答，保证演示环境可用。

## Learning Records

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/learning-records` | 登录用户 | 当前用户学习事件时间线。 |
| POST | `/api/learning-records` | 登录用户 | 手动写入学习事件。 |

## Reports

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/reports/me` | 登录用户 | 返回个人中心统计，包括课程数量、讨论互动、估算学习投入、进度、学习轨迹和建议。 |

## Error And Session Handling

- 未登录访问需要 token 的接口会返回 `401`。
- 身份不满足要求会返回 `403`。
- 删除成功一般返回 `204 No Content`。
- 前端收到 `401` 会清除本地 token 和用户信息，并跳转登录页。
