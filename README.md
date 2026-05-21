# LearnMate

`LearnMate` 是一个面向师生教学场景的智能学习伙伴平台。

当前技术栈：

```text
React + TypeScript + Vite
FastAPI
PostgreSQL + pgvector
Redis
MinIO
Docker Compose
```

## Current Features

- 登录注册，支持学生和伴学师两种身份。
- 游客可浏览课程、讨论和课件列表。
- 学生可加入或退出课程，使用 Markdown 和附件发布讨论，参与评论、点赞，删除自己的评论，上传个人头像，并使用带课程资料引用的 AI 伴学。
- 伴学师可创建、编辑、删除自己的课程，维护课程章节，上传和删除自己上传的课件，管理讨论区帖子和评论，并发送私信/公告。
- 后端提供 token 鉴权、角色权限检查、头像上传、课程选课、章节管理、文件上传限制、课程资料索引、论坛附件、论坛互动、消息提醒、学习事件、个人中心统计和 AI 问答接口。
- 前端使用 React Router 懒加载页面，统一 API 请求封装会自动携带 token、处理 401 和 204 响应。
- 讨论区列表支持长帖自动折叠，展开全文、点赞和评论操作统一放在帖子右下角；发帖页是独立页面，支持 Markdown 实时预览和最多 5 个附件。
- 顶部用户区支持圆形头像、头像上传和消息未读角标。
- 课件可绑定课程和章节，上传后会抽取文本并切分为知识库片段；AI 伴学会返回回答、会话 ID 和引用来源。
- 已加入 Alembic 迁移骨架和初始 schema，开发环境仍保留 `create_all()` 补列以兼容旧库。

## Project Structure

```text
apps/web      React 前端应用
apps/api      FastAPI 后端应用
packages      共享类型和工具
docs          项目设计文档
deploy        部署配置
data          示例数据和知识库资料
```

## Development

前端：

```bash
cd apps/web
npm install
npm run dev
```

后端：

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

基础服务：

```bash
cd deploy
docker compose up -d
```

Docker 全量启动：

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

仅前端源码改动时，Docker 部署不会热重载，需要重建 `web` 静态镜像：

```bash
docker compose -f deploy/docker-compose.yml up -d --build web
```

## Verification

前端构建：

```bash
npm run build --prefix apps/web
```

后端语法检查：

```bash
python3 -m compileall apps/api/app
```

后端测试：

```bash
cd apps/api
APP_ENV=test .venv/bin/python -m pytest tests
```

Alembic 离线 SQL 验证：

```bash
cd apps/api
APP_ENV=test .venv/bin/python -m alembic upgrade head --sql
```

## Notes

- `apps/api/.env.example` 适合本机开发；Docker Compose 场景建议从 `deploy/env.example` 复制到 `apps/api/.env`。
- `project_structure_1.md` 是当前项目结构说明，按目录和关键文件解释命名、作用和功能归属。
- 当前 AI 伴学支持本地 embedding + 关键词混合检索和引用来源；配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 后可调用 OpenAI 兼容大模型。pgvector 原生索引仍可作为后续增强。
- 当前文件上传默认使用后端本地目录；设置 `STORAGE_BACKEND=minio` 后可切换到 MinIO。
