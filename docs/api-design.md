# API Design

更新日期：2026-05-25

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
| GET | `/api/courses` | 可选 | 课程列表。游客和学生只返回已发布课程；伴学师返回已发布课程和自己创建的草稿；登录学生会额外返回本人是否已加入。 |
| POST | `/api/courses` | 伴学师 | 创建课程。 |
| GET | `/api/courses/{course_id}` | 可选 | 课程详情。已发布课程可公开查看；草稿课程仅创建它的伴学师可查看。 |
| PUT | `/api/courses/{course_id}` | 伴学师本人 | 编辑自己创建的课程。 |
| DELETE | `/api/courses/{course_id}` | 伴学师本人 | 删除自己创建的课程，返回 `204`。 |
| POST | `/api/courses/{course_id}/enroll` | 学生 | 加入课程。重复加入会保持幂等。 |
| DELETE | `/api/courses/{course_id}/enroll` | 学生 | 退出课程。未加入时保持幂等。 |
| GET | `/api/courses/{course_id}/enrollments` | 课程创建者 | 查看课程学生名单。 |
| DELETE | `/api/courses/{course_id}/enrollments/{enrollment_id}` | 课程创建者 | 从课程学生名单移除学生，返回 `204`。 |
| GET | `/api/courses/{course_id}/chapters` | 可选 | 查看课程章节目录，遵循课程可见性规则。 |
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

学生名单响应字段：

```text
id
course_id
student_id
student_name
created_at
```

课程可见性规则：

- `published` 课程可被游客、学生和伴学师访问。
- `draft` 课程只对创建它的伴学师可见。
- 学生端不会展示课程状态文案；草稿课程不会出现在学生列表、详情、章节、资料和讨论中。

## Forum

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/forum/posts` | 可选 | 帖子分页列表，游客可浏览。支持 `course_id`、`keyword`、`page`、`page_size`，伴学师可额外使用 `status_filter`。草稿课程关联帖子仅课程创建者可见。 |
| POST | `/api/forum/posts` | 学生/伴学师 | 发布帖子，使用 `multipart/form-data`，字段包含 `title`、`content`、可选 `course_id` 和最多 5 个 `attachments`。正文按 Markdown 文本保存，前端负责预览和展示渲染；草稿课程只允许课程创建者关联发帖。 |
| GET | `/api/forum/attachments/{stored_name}/download` | 可选 | 下载帖子附件，遵循帖子关联课程的可见性规则。 |
| GET | `/api/forum/posts/{post_id}/comments` | 游客 | 查看评论。 |
| POST | `/api/forum/posts/{post_id}/comments` | 学生/伴学师 | 发布评论。 |
| DELETE | `/api/forum/comments/{comment_id}` | 评论作者/伴学师 | 删除评论，返回 `204`。 |
| POST | `/api/forum/posts/{post_id}/like` | 学生/伴学师 | 切换点赞状态。 |
| DELETE | `/api/forum/posts/{post_id}` | 伴学师 | 删除帖子，返回 `204`。 |
| PATCH | `/api/forum/posts/{post_id}/status` | 伴学师 | 隐藏或恢复帖子，`status` 支持 `active` / `hidden`。 |

帖子列表响应为分页对象，包含 `items`、`total`、`page`、`page_size`。帖子响应包含 `like_count`、`comment_count`、`liked_by_me`、`author_avatar_url`、`attachments`、`course_title` 和 `status`；前端列表不再展示附带标签。评论响应包含 `author_avatar_url` 和 `can_delete`。点赞和评论会给帖子作者生成消息提醒，自己操作自己的帖子不会提醒自己。论坛附件当前使用后端本地 `storage/forum-attachments` 保存，下载接口会校验文件名避免路径穿越，并校验草稿课程可见性。

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
| GET | `/api/files` | 可选 | 课件列表，支持 `course_id` 和 `chapter_id` 筛选。草稿课程课件仅课程创建者可见。 |
| POST | `/api/files/upload` | 伴学师 | 上传课件。使用 `multipart/form-data`，支持可选 `course_id` 和 `chapter_id`，限制大小和 MIME 类型。 |
| GET | `/api/files/{file_id}/download` | 可选 | 浏览或下载课件，遵循课件关联课程的可见性规则。 |
| DELETE | `/api/files/{file_id}` | 上传者本人且为伴学师 | 删除自己上传的课件，返回 `204`。 |

当前默认上传限制：

```text
最大大小：20MB
允许类型：PDF、PNG、JPEG、TXT、DOCX
```

上传文本、Markdown、DOCX 和安装 `pypdf` 后的 PDF 会自动抽取文本、切分为知识库 chunk，用于智能伴学检索。`STORAGE_BACKEND=local` 使用本地目录；`STORAGE_BACKEND=minio` 使用 MinIO。

## Assistant

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/assistant/messages` | 学生/伴学师 | 发送智能伴学问题，返回回答和引用列表。 |

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

生产环境接入外部模型时，建议在该接口外层补充输入长度限制、单用户/单课程频率限制、模型输出 token 上限、拒答边界、日志审计和敏感信息脱敏。

## Learning Records

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/learning-records` | 登录用户 | 当前用户学习事件时间线。 |
| POST | `/api/learning-records` | 登录用户 | 手动写入学习事件。 |
| POST | `/api/learning-records/course-progress` | 学生 | 按课程累计真实浏览时长和最高浏览进度。 |

## Reports

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/reports/me` | 登录用户 | 返回个人中心统计，包括课程数量、讨论互动、真实学习时长、浏览进度、学习轨迹和建议。 |

学生角色返回学习报告，重点展示选课数量、讨论互动、智能伴学提问、真实学习时长、浏览进度、学习轨迹和学习建议。伴学师角色返回教学看板，重点展示建课数量、选课学生数、章节数、课件数、课程概览、教学动态和教学建议。

伴学师额外字段：

```text
student_count
chapter_count
course_summaries[].id
course_summaries[].title
course_summaries[].status
course_summaries[].enrollment_count
course_summaries[].chapter_count
course_summaries[].file_count
```

## Error And Session Handling

- 未登录访问需要 token 的接口会返回 `401`。
- 身份不满足要求会返回 `403`。
- 删除成功一般返回 `204 No Content`。
- 前端收到 `401` 会清除本地 token 和用户信息，并跳转登录页。
