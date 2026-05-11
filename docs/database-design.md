# Database Design

本文档用于记录数据库表设计。

当前后端仍主要通过 SQLAlchemy `create_all()` 初始化表结构，并在开发环境启动时执行少量补丁 SQL。项目已引入 Alembic，但正式迁移版本仍待补齐。

## Current Tables

```text
users
courses
course_enrollments
forum_posts
forum_comments
forum_likes
file_assets
learning_events
learning_reports
assistant_sessions
```

## users

| Field | Description |
|---|---|
| id | 主键 |
| username | 唯一用户名，登录和展示使用 |
| password_hash | 密码哈希 |
| role | `student` 或 `mentor` |

## courses

| Field | Description |
|---|---|
| id | 主键 |
| title | 课程标题 |
| description | 课程介绍 |
| teacher_id | 创建课程的伴学师 ID |
| teacher_name | 创建课程的伴学师用户名 |
| status | 课程状态，当前常用 `published` / `draft` |
| created_at | 创建时间 |
| updated_at | 更新时间 |

## course_enrollments

学生选课关系表。

| Field | Description |
|---|---|
| id | 主键 |
| course_id | 课程 ID，关联 `courses.id`，课程删除时级联删除 |
| student_id | 学生 ID |
| student_name | 学生用户名快照 |
| created_at | 加入时间 |

约束和索引：

```text
UNIQUE(course_id, student_id)
INDEX(course_id)
INDEX(student_id)
```

## forum_posts

| Field | Description |
|---|---|
| id | 主键 |
| title | 帖子标题 |
| content | 帖子正文 |
| author_id | 作者 ID |
| author_name | 作者用户名快照 |
| course_id | 可选课程 ID |
| created_at | 创建时间 |

## forum_comments

| Field | Description |
|---|---|
| id | 主键 |
| post_id | 帖子 ID，关联 `forum_posts.id`，帖子删除时级联删除 |
| author_id | 评论作者 ID |
| author_name | 评论作者用户名快照 |
| content | 评论内容 |
| created_at | 创建时间 |

## forum_likes

| Field | Description |
|---|---|
| id | 主键 |
| post_id | 帖子 ID，关联 `forum_posts.id`，帖子删除时级联删除 |
| user_id | 点赞用户 ID |

约束：

```text
UNIQUE(post_id, user_id)
```

## file_assets

| Field | Description |
|---|---|
| id | 主键 |
| original_name | 用户上传时的原始文件名 |
| stored_name | 后端本地存储文件名 |
| content_type | MIME 类型 |
| size | 文件大小，单位字节 |
| uploader_id | 上传者 ID |
| uploader_name | 上传者用户名快照 |
| created_at | 上传时间 |

当前文件内容存放在后端本地上传目录，数据库只保存元数据。MinIO 配置已预留，尚未切换到对象存储。

## learning_events

| Field | Description |
|---|---|
| id | 主键 |
| user_id | 用户 ID |
| course_id | 可选课程 ID |
| event_type | 学习事件类型 |

该表已预留，但课程、论坛、AI 等行为还没有完整写入学习记录。

## learning_reports

| Field | Description |
|---|---|
| id | 主键 |
| user_id | 用户 ID |
| course_id | 可选课程 ID |
| summary | 报告摘要 |

当前报告能力仍偏占位，前端个人中心也还未接入真实统计数据。

## Planned Tables

后续 RAG、课程章节和学习数据闭环建议补充：

```text
course_chapters
course_materials
assistant_messages
knowledge_documents
knowledge_chunks
```

下一步建议把当前 schema 固化为第一版 Alembic migration，避免继续依赖启动时补丁 SQL。
