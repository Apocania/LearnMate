# LearnMate API

更新日期：2026-05-25

LearnMate 的 FastAPI 后端应用。

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

访问：

```text
http://localhost:8000/api/health
http://localhost:8000/docs
```

## Configuration

常用环境变量在 `.env.example` 中维护。当前后端会读取数据库、Redis、JWT、CORS、存储后端、MinIO、大模型和上传限制配置。

上传相关默认值：

```text
UPLOAD_MAX_SIZE_MB=200
UPLOAD_ALLOWED_TYPES=application/pdf,image/png,image/jpeg,image/webp,text/plain,text/markdown,text/csv,application/csv,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/zip,application/x-zip-compressed,video/mp4
UPLOAD_ALLOWED_EXTENSIONS=.pdf,.png,.jpg,.jpeg,.webp,.txt,.md,.csv,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.mp4
STORAGE_BACKEND=local
```

本机开发可从 `apps/api/.env.example` 复制 `.env`；Docker Compose 运行时建议从 `deploy/env.example` 复制到 `apps/api/.env`，因为容器网络中的数据库、Redis、MinIO 主机名分别是 `postgres`、`redis`、`minio`。

## Main Modules

- `auth/users`：注册、登录、当前用户解析、可选用户解析、角色权限工具和个人头像上传。用户名会去空格、小写化，并限制为 3-32 位英文、数字或下划线。
- `courses`：课程浏览、伴学师课程管理、学生加入/退出课程、课程学生名单管理、章节目录维护，响应会返回 `enrollment_count` 和 `joined_by_me`。草稿课程仅创建它的伴学师可见。
- `forum`：游客浏览帖子和评论，支持分页、课程筛选、关键词搜索。登录用户使用 Markdown 正文和最多 5 个附件发帖、评论、点赞并删除自己的评论，伴学师可隐藏、恢复、删除帖子和评论；草稿课程关联帖子仅课程创建者可见。
- `messages`：登录用户查看消息和未读数；点赞/评论会给帖子作者生成提醒；伴学师可发送私信和面向学生的公告。
- `files`：课件列表、上传、下载、删除。课件可绑定课程和章节，上传后会抽取文本并写入知识库 chunk。只有伴学师可上传，且只能删除自己上传的课件；草稿课程课件仅课程创建者可见。
- `assistant`：登录后调用 `/api/assistant/messages`，按课程资料检索知识库，返回回答、会话 ID 和引用来源；配置大模型后使用 OpenAI 兼容接口，否则使用本地检索式回答。
- `reports`：登录后返回个人中心统计。学生获得学习报告；伴学师获得教学看板数据，包括课程数、学生数、章节数、课件数、课程概览、教学动态和建议。
- `learning_records`：统一记录选课、发帖、评论、点赞、上传资料、AI 提问等学习事件，并提供个人时间线接口。

## API Summary

```text
POST   /api/auth/register
POST   /api/auth/login
GET    /api/users/me
POST   /api/users/me/avatar
GET    /api/courses
POST   /api/courses
GET    /api/courses/{course_id}
PUT    /api/courses/{course_id}
DELETE /api/courses/{course_id}
POST   /api/courses/{course_id}/enroll
DELETE /api/courses/{course_id}/enroll
GET    /api/courses/{course_id}/enrollments
DELETE /api/courses/{course_id}/enrollments/{enrollment_id}
GET    /api/courses/{course_id}/chapters
POST   /api/courses/{course_id}/chapters
PUT    /api/courses/{course_id}/chapters/{chapter_id}
DELETE /api/courses/{course_id}/chapters/{chapter_id}
GET    /api/forum/posts
POST   /api/forum/posts
GET    /api/forum/attachments/{stored_name}/download
GET    /api/forum/posts/{post_id}/comments
POST   /api/forum/posts/{post_id}/comments
DELETE /api/forum/comments/{comment_id}
POST   /api/forum/posts/{post_id}/like
DELETE /api/forum/posts/{post_id}
PATCH  /api/forum/posts/{post_id}/status
GET    /api/messages
GET    /api/messages/unread-count
GET    /api/messages/student-recipients
POST   /api/messages/{message_id}/read
POST   /api/messages/read-all
POST   /api/messages/private
POST   /api/messages/announcements
GET    /api/files
POST   /api/files/upload
GET    /api/files/{file_id}/download
DELETE /api/files/{file_id}
POST   /api/assistant/messages
GET    /api/learning-records
POST   /api/learning-records
GET    /api/reports/me
```

## Tests

测试依赖已写入 `requirements.txt`。运行：

```bash
APP_ENV=test .venv/bin/python -m pytest tests
```

`APP_ENV=test` 会跳过启动时的数据库初始化，便于运行不依赖真实数据库的轻量测试。

## Demo Data

截图展示前可运行演示数据脚本，它会生成儿童学习主题课程、章节、课件、讨论、评论、消息、AI 会话、学习轨迹和演示头像：

```bash
.venv/bin/python scripts/seed_demo_data.py
```

演示账号：`demo_student / password123`，`demo_mentor / password123`。

脚本会写入本地数据库并生成少量本地课件文本文件；重复运行会更新演示账号、课程和部分演示记录，适合作为截图前的数据重置入口。

## Storage Notes

当前后端上传分为三类：

- 个人头像：写入后端本地头像目录，并通过用户 `avatar_url` 返回给前端。
- 课件文件：默认写入后端本地上传目录，数据库保存文件元数据；`STORAGE_BACKEND=minio` 时会写入 MinIO。文本、Markdown、DOCX 和安装 `pypdf` 后的 PDF 会进入 AI 知识库。
- 论坛附件：写入 `storage/forum-attachments`，帖子表保存附件 JSON 元数据和下载地址。

MinIO 配置和 Compose 服务已经预留。Docker 场景建议使用 `STORAGE_BACKEND=minio`，本机开发默认 `local`，便于不启动 MinIO 时也能跑完整闭环。

## 智能伴学说明

智能伴学当前已经具备轻量 RAG 闭环：课件上传后抽取文本、切分 chunk、写入知识库；提问时按课程资料做本地 embedding + 关键词混合检索，并返回引用来源。未配置大模型时使用本地检索式回答；配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 后会调用 OpenAI 兼容接口。

接入真实模型前建议继续补齐：输入长度限制、每用户限流、`max_tokens`、拒答边界、输出安全检查和模型调用审计。
