# LearnMate API

LearnMate 的 FastAPI 后端应用。

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

访问：

```text
http://localhost:8000/api/health
http://localhost:8000/docs
```

## Configuration

常用环境变量在 `.env.example` 中维护。当前后端会读取数据库、Redis、JWT、CORS、MinIO、大模型和上传限制配置。

上传相关默认值：

```text
UPLOAD_MAX_SIZE_MB=20
UPLOAD_ALLOWED_TYPES=application/pdf,image/png,image/jpeg,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

本机开发可从 `apps/api/.env.example` 复制 `.env`；Docker Compose 运行时建议从 `deploy/env.example` 复制到 `apps/api/.env`，因为容器网络中的数据库、Redis、MinIO 主机名分别是 `postgres`、`redis`、`minio`。

## Main Modules

- `auth`：注册、登录、当前用户解析、可选用户解析和角色权限工具。用户名会去空格、小写化，并限制为 3-32 位英文、数字或下划线。
- `courses`：课程浏览、伴学师课程管理、学生加入/退出课程，响应会返回 `enrollment_count` 和 `joined_by_me`。
- `forum`：游客浏览帖子和评论，登录用户发帖、评论、点赞，伴学师可删除帖子。
- `files`：课件列表、上传、下载、删除。只有伴学师可上传，且只能删除自己上传的课件。
- `assistant`：登录后调用 `/api/assistant/messages`，当前仍使用占位检索和占位模型回答。
- `learning_records` / `reports`：学习记录和报告模块已预留，真实数据闭环仍待完善。

## API Summary

```text
POST   /api/auth/register
POST   /api/auth/login
GET    /api/courses
POST   /api/courses
GET    /api/courses/{course_id}
PUT    /api/courses/{course_id}
DELETE /api/courses/{course_id}
POST   /api/courses/{course_id}/enroll
DELETE /api/courses/{course_id}/enroll
GET    /api/forum/posts
POST   /api/forum/posts
GET    /api/forum/posts/{post_id}/comments
POST   /api/forum/posts/{post_id}/comments
POST   /api/forum/posts/{post_id}/like
DELETE /api/forum/posts/{post_id}
GET    /api/files
POST   /api/files/upload
GET    /api/files/{file_id}/download
DELETE /api/files/{file_id}
POST   /api/assistant/messages
```

## Tests

测试依赖已写入 `requirements.txt`。运行：

```bash
APP_ENV=test .venv/bin/python -m pytest tests
```

`APP_ENV=test` 会跳过启动时的数据库初始化，便于运行不依赖真实数据库的轻量测试。
