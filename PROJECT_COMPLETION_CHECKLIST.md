# LearnMate Completion Checklist

整理日期：2026-05-15  
项目阶段：可演示的早期原型，核心教学业务链路已经打通，但距离生产级系统仍有明显缺口。

本文档用于回答三个问题：

1. 当前已经完成了什么。
2. 每个已完成功能由哪些模块和文件实现。
3. 还没有完成什么，以及下一步应该如何完成。

## 1. 总体状态

| Area | Status | Summary |
|---|---|---|
| 前端应用 | 已完成核心页面 | React + TypeScript + Vite 单页应用已可运行，页面路由、顶部导航、登录态、头像、消息红点和主要业务页面已实现。 |
| 后端应用 | 已完成核心 API | FastAPI + SQLAlchemy 后端已实现认证、课程、论坛、文件、消息、报告和 AI 问答接口边界。 |
| 课程业务 | 基本完成 | 游客浏览、伴学师建课/改课/删课、学生加入/退出课程已实现。 |
| 论坛业务 | 基本完成 | Markdown 发帖、附件、长帖折叠、评论、点赞、评论删除、伴学师管理、消息提醒已实现。 |
| 文件业务 | 基本完成 | 课件上传、列表、下载、删除和文件类型/大小限制已实现，但仍是本地存储。 |
| 消息业务 | 基本完成 | 点赞提醒、评论提醒、私信、公告、未读数和已读状态已实现。 |
| AI 伴学 | 接口打通，智能能力未完成 | 前后端链路存在，但向量检索和大模型调用仍是占位。 |
| 学习报告 | 轻量完成 | 已基于课程和论坛数据生成统计，但缺真实学习事件闭环。 |
| 部署 | 可本地 Docker 演示 | Docker Compose 可启动 PostgreSQL、Redis、MinIO、API、Web，但生产化不足。 |
| 测试 | 基础完成 | 有少量后端测试；前端、端到端和核心权限测试仍不足。 |

## 2. 已完成清单

### 2.1 项目骨架和工程结构

状态：已完成。

已实现内容：

- 使用 monorepo 结构组织前端、后端、部署、文档和数据目录。
- 根目录提供 npm workspace 和前端构建脚本。
- 项目文档已经覆盖总览、API、数据库、AI、部署和结构说明。

实现位置：

| Part | Files |
|---|---|
| 根项目说明 | `README.md` |
| 项目审查报告 | `PROJECT_REVIEW.md` |
| 结构说明 | `project_structure_1.md` |
| 前端应用 | `apps/web/` |
| 后端应用 | `apps/api/` |
| 部署配置 | `deploy/` |
| 设计文档 | `docs/` |
| npm workspace | `package.json`, `package-lock.json` |

验收方式：

- 能从根目录识别项目组成。
- 能通过 README 找到本地开发、Docker 启动和验证命令。
- 能通过结构文档定位每个功能模块。

### 2.2 前端路由和应用布局

状态：已完成。

已实现内容：

- 前端采用 React Router。
- 页面通过 `React.lazy` 和 `Suspense` 懒加载。
- 顶部导航包含课程中心、讨论交流、AI 伴学、消息中心、个人中心。
- 登录后右上角显示圆形头像、用户名、角色和退出按钮。
- 未登录时显示登录按钮。
- 消息中心导航项带未读红点。

实现位置：

| Part | Files |
|---|---|
| 路由表 | `apps/web/src/app/router.tsx` |
| 应用 Provider | `apps/web/src/app/providers.tsx` |
| 主布局和导航 | `apps/web/src/components/AppLayout.tsx` |
| 用户头像组件 | `apps/web/src/components/UserAvatar.tsx` |
| 全局样式 | `apps/web/src/styles.css` |
| 前端入口 | `apps/web/src/main.tsx` |

验收方式：

- 访问 `/courses`、`/forum`、`/forum/new`、`/files`、`/assistant`、`/messages`、`/reports/me` 能进入对应页面。
- 登录后右上角不再显示登录按钮，而是显示用户头像和退出按钮。
- 消息未读数会显示在消息中心导航处。

### 2.3 登录注册和角色权限

状态：已完成核心能力。

已实现内容：

- 支持注册和登录。
- 支持 `student` 和 `mentor` 两种角色。
- 用户名会去空格、小写化，并限制为 3-32 位英文、数字、下划线。
- 后端使用 token 鉴权。
- 前端请求会自动携带 token。
- 前端收到 `401` 会清理登录态并跳转登录页。
- 游客可浏览公开内容，学生和伴学师拥有不同操作权限。

实现位置：

| Part | Files |
|---|---|
| 后端用户模型 | `apps/api/app/modules/auth/models.py` |
| 后端认证接口 | `apps/api/app/modules/auth/api.py` |
| 后端认证服务 | `apps/api/app/modules/auth/service.py` |
| 后端认证依赖 | `apps/api/app/modules/auth/dependencies.py` |
| 后端安全工具 | `apps/api/app/core/security.py` |
| 前端登录注册页 | `apps/web/src/pages/LoginPage.tsx` |
| 前端认证 API | `apps/web/src/api/auth.ts` |
| 前端请求封装 | `apps/web/src/api/client.ts` |
| 前端登录态工具 | `apps/web/src/shared/utils/currentUser.ts` |
| 当前用户 Hook | `apps/web/src/shared/utils/useCurrentUser.ts` |

验收方式：

- 能注册学生和伴学师。
- 学生不能创建课程。
- 伴学师能进入课程管理和消息发送能力。
- token 失效后前端会回到登录页。

### 2.4 用户头像

状态：已完成。

已实现内容：

- 登录用户可上传头像。
- 支持 JPG、PNG、WebP、GIF。
- 上传后后端更新用户 `avatar_url`。
- 前端顶部头像、帖子作者头像、评论作者头像会显示真实头像。
- 没有头像时显示用户名首字母占位。

实现位置：

| Part | Files |
|---|---|
| 后端用户接口 | `apps/api/app/modules/users/api.py` |
| 后端头像服务 | `apps/api/app/modules/users/service.py` |
| 用户表字段 | `apps/api/app/modules/auth/models.py` |
| 初始化补丁字段 | `apps/api/app/core/init_db.py` |
| 前端头像上传入口 | `apps/web/src/components/AppLayout.tsx` |
| 前端头像组件 | `apps/web/src/components/UserAvatar.tsx` |
| 前端认证 API | `apps/web/src/api/auth.ts` |

验收方式：

- 点击右上角用户头像能打开头像弹窗。
- 上传图片后，顶部头像立即刷新。
- 帖子和评论中能看到用户头像。

### 2.5 课程中心

状态：基本完成。

已实现内容：

- 游客可浏览课程。
- 伴学师可创建、编辑、删除自己创建的课程。
- 学生可加入和退出课程。
- 课程响应包含教师、状态、选课人数和本人是否已加入。
- 课程详情页展示课程信息和加入状态。

实现位置：

| Part | Files |
|---|---|
| 后端课程模型 | `apps/api/app/modules/courses/models.py` |
| 后端课程接口 | `apps/api/app/modules/courses/api.py` |
| 后端课程服务 | `apps/api/app/modules/courses/service.py` |
| 后端课程仓储 | `apps/api/app/modules/courses/repository.py` |
| 后端课程 schema | `apps/api/app/modules/courses/schemas.py` |
| 前端课程 API | `apps/web/src/api/courses.ts` |
| 课程列表页 | `apps/web/src/pages/CourseListPage.tsx` |
| 课程详情页 | `apps/web/src/pages/CourseDetailPage.tsx` |

验收方式：

- 游客能看到课程列表。
- 学生看到加入/退出课程操作。
- 伴学师看到创建、编辑、删除课程操作。
- 学生登录后不会看到创建课程选项。

### 2.6 讨论交流论坛

状态：基本完成。

已实现内容：

- 游客可浏览帖子和评论。
- 登录用户可发布帖子。
- 发帖页是独立页面，不再是简陋弹窗。
- 发帖支持标题、Markdown 正文和附件。
- Markdown 支持标题、列表、加粗、斜体、行内代码。
- 发帖页提供实时预览。
- 帖子最多支持 5 个附件。
- 帖子列表中长正文自动折叠，保持列表浏览时高度稳定。
- 展开全文、点赞、评论三个操作统一放在帖子右下角。
- 评论区在帖子内展开。
- 登录用户可评论、点赞。
- 用户可删除自己的评论。
- 伴学师可删除帖子和任意评论。
- 点赞和评论会给帖子作者生成消息提醒。

实现位置：

| Part | Files |
|---|---|
| 后端论坛模型 | `apps/api/app/modules/forum/models.py` |
| 后端论坛接口 | `apps/api/app/modules/forum/api.py` |
| 后端论坛服务 | `apps/api/app/modules/forum/service.py` |
| 后端论坛仓储 | `apps/api/app/modules/forum/repository.py` |
| 后端论坛 schema | `apps/api/app/modules/forum/schemas.py` |
| 消息提醒调用 | `apps/api/app/modules/messages/service.py` |
| 前端论坛 API | `apps/web/src/api/forum.ts` |
| 论坛列表页 | `apps/web/src/pages/ForumPage.tsx` |
| 独立发帖页 | `apps/web/src/pages/ForumPostEditorPage.tsx` |
| Markdown 工具 | `apps/web/src/shared/utils/markdown.ts` |
| 论坛和编辑器样式 | `apps/web/src/styles.css` |

验收方式：

- 点击发布帖子进入 `/forum/new`。
- 能输入标题、Markdown 正文并看到实时预览。
- 发布后返回论坛列表。
- 长帖默认折叠，点击展开全文后显示完整内容。
- 点赞、评论、展开全文横向对齐在帖子右下角。
- 自己发布的评论能删除。
- 伴学师能删除评论和帖子。

### 2.7 消息中心

状态：基本完成。

已实现内容：

- 登录用户可查看消息列表。
- 顶部导航显示未读消息数。
- 支持单条消息标记已读。
- 支持全部标记已读。
- 点赞帖子会生成点赞提醒。
- 评论帖子会生成评论提醒。
- 自己操作自己的帖子不会提醒自己。
- 伴学师可向学生发送私信。
- 伴学师可向所有学生发送公告。

实现位置：

| Part | Files |
|---|---|
| 后端消息模型 | `apps/api/app/modules/messages/models.py` |
| 后端消息接口 | `apps/api/app/modules/messages/api.py` |
| 后端消息服务 | `apps/api/app/modules/messages/service.py` |
| 后端消息仓储 | `apps/api/app/modules/messages/repository.py` |
| 后端消息 schema | `apps/api/app/modules/messages/schemas.py` |
| 前端消息 API | `apps/web/src/api/messages.ts` |
| 前端消息页面 | `apps/web/src/pages/MessagesPage.tsx` |
| 未读角标刷新 | `apps/web/src/components/AppLayout.tsx` |

验收方式：

- 学生收到点赞、评论、私信、公告后消息中心出现记录。
- 顶部消息角标显示未读数。
- 伴学师能发送私信和公告。
- 学生不能发送私信和公告。

### 2.8 文件资料

状态：基本完成。

已实现内容：

- 游客和学生可浏览课件。
- 伴学师可上传课件。
- 伴学师可删除自己上传的课件。
- 所有用户可下载课件。
- 后端校验文件大小和 MIME 类型。
- 文件名使用 UUID 存储，避免重名覆盖。

实现位置：

| Part | Files |
|---|---|
| 后端文件模型 | `apps/api/app/modules/files/models.py` |
| 后端文件接口 | `apps/api/app/modules/files/api.py` |
| 后端文件服务 | `apps/api/app/modules/files/service.py` |
| 后端文件仓储 | `apps/api/app/modules/files/repository.py` |
| 后端文件 schema | `apps/api/app/modules/files/schemas.py` |
| 前端文件 API | `apps/web/src/api/files.ts` |
| 前端文件页面 | `apps/web/src/pages/FilesPage.tsx` |
| 上传限制配置 | `apps/api/app/core/config.py` |

验收方式：

- 游客能看到课件列表并下载。
- 学生不能上传课件。
- 伴学师能上传课件。
- 上传不支持类型或超大文件会失败。

### 2.9 AI 伴学页面和接口边界

状态：部分完成。

已实现内容：

- 前端有 AI 伴学聊天页面。
- 登录用户可发送问题。
- 游客看到登录提示。
- 后端有 `/api/assistant/messages` 接口。
- 后端已经拆出检索、Prompt、LLM 客户端等边界。

实现位置：

| Part | Files |
|---|---|
| 前端 AI 页面 | `apps/web/src/pages/AssistantPage.tsx` |
| 前端 AI API | `apps/web/src/api/assistant.ts` |
| 后端 AI 接口 | `apps/api/app/modules/assistant/api.py` |
| 对话编排服务 | `apps/api/app/modules/assistant/chat_service.py` |
| 检索服务 | `apps/api/app/modules/assistant/retrieval_service.py` |
| Prompt 构造 | `apps/api/app/modules/assistant/prompt_builder.py` |
| 向量库占位 | `apps/api/app/infrastructure/vector_store.py` |
| LLM 客户端占位 | `apps/api/app/infrastructure/llm_client.py` |

当前限制：

- 没有真实大模型回答。
- 没有真实课程资料检索。
- 没有引用来源。
- 没有流式输出。
- 没有对话历史落库。

### 2.10 个人中心和学习报告

状态：轻量完成。

已实现内容：

- 登录用户可访问个人中心/学习报告。
- 后端返回课程数量、讨论互动、估算学习投入、进度、学习轨迹和建议。
- 统计当前主要基于课程和论坛数据。

实现位置：

| Part | Files |
|---|---|
| 后端报告模型 | `apps/api/app/modules/reports/models.py` |
| 后端报告接口 | `apps/api/app/modules/reports/api.py` |
| 后端报告服务 | `apps/api/app/modules/reports/service.py` |
| 后端报告仓储 | `apps/api/app/modules/reports/repository.py` |
| 后端报告 schema | `apps/api/app/modules/reports/schemas.py` |
| 前端报告 API | `apps/web/src/api/reports.ts` |
| 前端报告页面 | `apps/web/src/pages/LearningReportPage.tsx` |

验收方式：

- 登录用户能进入 `/reports/me`。
- 页面能展示课程、讨论和建议统计。

### 2.11 Docker 部署

状态：可本地演示。

已实现内容：

- Docker Compose 定义 PostgreSQL、Redis、MinIO、API、Web。
- 前端容器使用 nginx 托管构建后的静态文件。
- 后端容器读取 `apps/api/.env`。
- 提供 Docker 启动和只重建前端的文档说明。

实现位置：

| Part | Files |
|---|---|
| Compose 配置 | `deploy/docker-compose.yml` |
| Docker 环境变量模板 | `deploy/env.example` |
| 前端 Dockerfile | `apps/web/Dockerfile` |
| 前端 nginx 配置 | `apps/web/nginx.conf` |
| 后端 Dockerfile | `apps/api/Dockerfile` |
| 部署文档 | `deploy/README.md`, `docs/deployment.md` |

验收方式：

- `docker compose -f deploy/docker-compose.yml up -d --build` 能启动服务。
- 前端访问 `http://localhost:5173`。
- 后端访问 `http://localhost:8000/docs`。

### 2.12 基础测试

状态：基础完成。

已实现内容：

- 后端有健康检查测试。
- 有注册用户名校验测试。
- 有头像上传相关测试。
- 有消息接口相关测试。
- 有个人报告接口测试。

实现位置：

| Part | Files |
|---|---|
| 健康检查测试 | `apps/api/tests/test_health.py` |
| 认证校验测试 | `apps/api/tests/test_auth_validation.py` |
| 头像测试 | `apps/api/tests/test_users_avatar.py` |
| 消息测试 | `apps/api/tests/test_messages.py` |
| 报告测试 | `apps/api/tests/test_reports.py` |

验收方式：

```bash
APP_ENV=test apps/api/.venv/bin/python -m pytest apps/api/tests
```

## 3. 待完成清单

### 3.1 接入真实 AI 大模型

优先级：高。

当前问题：

- `LLMClient.chat()` 仍是占位实现。
- 用户看到的是模板化回答，不是真实 AI 推理结果。

应该如何完成：

1. 在 `apps/api/app/infrastructure/llm_client.py` 中实现真实 OpenAI-compatible 调用。
2. 在 `apps/api/app/core/config.py` 中完善 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL` 配置校验。
3. 在 `apps/api/app/modules/assistant/chat_service.py` 中处理模型异常、超时和空回答。
4. 前端 `AssistantPage.tsx` 增加加载状态、失败重试和错误提示。
5. 为 `assistant` 模块增加后端测试，覆盖未登录、空问题、模型失败和成功回答。

建议涉及文件：

```text
apps/api/app/infrastructure/llm_client.py
apps/api/app/core/config.py
apps/api/app/modules/assistant/chat_service.py
apps/api/app/modules/assistant/api.py
apps/web/src/pages/AssistantPage.tsx
apps/api/tests/
```

验收标准：

- 配置真实 API Key 后，AI 伴学能返回真实模型回答。
- 模型服务不可用时，前端显示友好错误。
- 后端不会把 API Key 输出到日志或响应中。

### 3.2 完成 RAG 知识库检索

优先级：高。

当前问题：

- `VectorStore.search()` 是占位。
- 上传课件后没有解析、切片、embedding 和入库。
- AI 回答没有真实引用来源。

应该如何完成：

1. 设计 `knowledge_documents` 和 `knowledge_chunks` 表。
2. 使用 Alembic 新增迁移。
3. 在课件上传后触发文本解析流程，支持 PDF、TXT、DOCX。
4. 将文本按课程、文件、章节切片。
5. 调用 embedding 模型生成向量。
6. 使用 pgvector 保存 chunk 向量。
7. 在 `VectorStore.search()` 中按 `course_id` 和 query embedding 检索相似 chunk。
8. `prompt_builder.py` 将检索结果拼入 prompt。
9. `AssistantMessageResponse.citations` 返回文件名、片段、页码或 chunk 信息。

建议涉及文件：

```text
apps/api/app/modules/assistant/knowledge_ingestion.py
apps/api/app/modules/assistant/retrieval_service.py
apps/api/app/infrastructure/vector_store.py
apps/api/app/modules/assistant/prompt_builder.py
apps/api/app/modules/files/service.py
apps/api/app/modules/assistant/models.py
docs/ai-assistant-design.md
docs/database-design.md
```

验收标准：

- 上传课程资料后能在数据库看到文档和 chunk。
- AI 提问能基于相关资料回答。
- 回答包含可展示的引用来源。

### 3.3 建立正式 Alembic 数据库迁移

优先级：高。

当前问题：

- 当前仍依赖 `Base.metadata.create_all()` 和 `init_db.py` 中的补丁 SQL。
- 随着字段增加，生产环境升级风险很高。

应该如何完成：

1. 初始化 Alembic 配置。
2. 生成当前数据库结构的第一版 baseline migration。
3. 将 `init_db.py` 中的开发期 `ALTER TABLE` 补丁固化为 migration。
4. 启动时不再依赖补丁 SQL 修改生产 schema。
5. 测试环境保留轻量初始化方式，或单独使用测试迁移。
6. 文档中明确迁移命令和回滚方式。

建议涉及文件：

```text
apps/api/migrations/
apps/api/alembic.ini
apps/api/app/core/init_db.py
apps/api/app/core/database.py
docs/database-design.md
docs/deployment.md
```

验收标准：

- 新环境能通过 migration 建表。
- 老环境能通过 migration 平滑升级。
- 不再需要在生产启动时执行临时补丁 SQL。

### 3.4 切换上传文件到 MinIO

优先级：高。

当前问题：

- 课件、头像、论坛附件都写在后端本地磁盘。
- Docker Compose 虽然启动 MinIO，但业务代码没有真正使用。
- 容器重建或多实例部署时，本地文件容易丢失或不一致。

应该如何完成：

1. 在 `object_storage.py` 中实现 MinIO 客户端。
2. 定义统一上传接口：保存文件、删除文件、生成下载 URL。
3. 改造 `files/service.py`、`users/service.py`、`forum/service.py` 使用对象存储。
4. 数据库保存对象 key、原始文件名、MIME、大小和 bucket。
5. 对私有文件使用后端代理下载或短期签名 URL。
6. 增加迁移脚本，把已有本地文件迁移到 MinIO。

建议涉及文件：

```text
apps/api/app/infrastructure/object_storage.py
apps/api/app/modules/files/service.py
apps/api/app/modules/users/service.py
apps/api/app/modules/forum/service.py
apps/api/app/core/config.py
deploy/docker-compose.yml
docs/deployment.md
```

验收标准：

- 上传后的文件能在 MinIO bucket 中看到。
- 删除课件会同步删除对象。
- 重建 API 容器后已上传文件仍可下载。

### 3.5 完善学习记录闭环

优先级：高。

当前问题：

- `learning_records` 模块目前主要是预留。
- 学习报告没有真实学习事件来源。
- AI 提问、课件下载、课程学习等行为没有完整记录。

应该如何完成：

1. 设计统一学习事件类型，例如 `course_enrolled`、`file_downloaded`、`forum_posted`、`assistant_asked`。
2. 在课程、文件、论坛、AI 模块调用 `LearningRecordService` 写入事件。
3. 为事件增加时间、课程、对象类型、对象 ID、元数据。
4. 改造 `reports/service.py` 基于学习事件计算投入、进度和建议。
5. 前端报告页展示更具体的学习轨迹。

建议涉及文件：

```text
apps/api/app/modules/learning_records/
apps/api/app/modules/courses/service.py
apps/api/app/modules/files/service.py
apps/api/app/modules/forum/service.py
apps/api/app/modules/assistant/chat_service.py
apps/api/app/modules/reports/service.py
apps/web/src/pages/LearningReportPage.tsx
```

验收标准：

- 用户加入课程、下载文件、发帖、评论、AI 提问后能生成学习事件。
- 个人中心能展示真实事件时间线。
- 报告统计不再只依赖粗略估算。

### 3.6 增加课程章节和课件绑定

优先级：中高。

当前问题：

- 课程只有标题、描述、教师和状态。
- 没有章节、课时、任务和课程资料归属。
- 课件资料是全局列表，未绑定课程。

应该如何完成：

1. 新增 `course_chapters` 表，包含课程 ID、标题、排序、描述。
2. 新增 `course_materials` 或扩展 `file_assets`，绑定课程和章节。
3. 后端提供章节 CRUD 和课程资料接口。
4. 伴学师在课程详情页维护章节和资料。
5. 学生在课程详情页按章节查看资料和学习进度。
6. AI 检索时按课程资料过滤知识库。

建议涉及文件：

```text
apps/api/app/modules/courses/
apps/api/app/modules/files/
apps/web/src/pages/CourseDetailPage.tsx
apps/web/src/pages/FilesPage.tsx
docs/api-design.md
docs/database-design.md
```

验收标准：

- 伴学师能给课程添加章节。
- 课件能绑定到课程或章节。
- 学生进入课程详情能按章节查看资料。

### 3.7 完善论坛高级能力

优先级：中。

当前问题：

- 没有分页。
- 没有搜索。
- 没有按课程筛选。
- 帖子不能编辑。
- 删除是硬删除。
- 没有举报、审核和内容安全机制。

应该如何完成：

1. 后端 `list_posts` 增加分页参数 `page`、`page_size`。
2. 增加 `course_id`、关键词、作者等筛选条件。
3. 新增帖子编辑接口，只允许作者或伴学师按规则操作。
4. 将硬删除改为软删除字段，例如 `deleted_at`、`deleted_by`。
5. 新增举报表和审核状态。
6. 前端论坛页增加搜索框、筛选器、分页器和编辑入口。

建议涉及文件：

```text
apps/api/app/modules/forum/
apps/web/src/pages/ForumPage.tsx
apps/web/src/pages/ForumPostEditorPage.tsx
apps/web/src/api/forum.ts
docs/api-design.md
docs/database-design.md
```

验收标准：

- 帖子列表分页稳定。
- 能按课程筛选帖子。
- 作者能编辑自己的帖子。
- 删除后数据仍可审计。

### 3.8 消息实时推送和来源跳转

优先级：中。

当前问题：

- 当前未读数通过前端每 30 秒轮询。
- 消息没有实时推送。
- 消息点击后没有完整跳转到来源对象。
- 公告只能面向所有学生，不能按课程或分组发送。

应该如何完成：

1. 增加 WebSocket 或 SSE 消息推送。
2. 后端消息创建后推送给在线用户。
3. 前端替换或补充轮询机制。
4. 根据 `source_type` 和 `source_id` 实现消息点击跳转。
5. 公告增加课程维度、角色维度或指定学生分组。

建议涉及文件：

```text
apps/api/app/modules/messages/
apps/web/src/pages/MessagesPage.tsx
apps/web/src/components/AppLayout.tsx
apps/web/src/api/messages.ts
```

验收标准：

- 收到点赞或评论时，消息红点无需等待 30 秒刷新。
- 点击评论提醒能定位到对应帖子。
- 伴学师能给某门课程的学生发公告。

### 3.9 文件资料预览、分类和权限细化

优先级：中。

当前问题：

- 文件只有全局列表。
- 没有课程绑定、分类、预览和版本。
- 文件下载权限较粗。

应该如何完成：

1. 文件绑定课程和章节。
2. 增加文件分类，例如课件、作业、参考资料。
3. 支持 PDF 或图片在线预览。
4. 为文件增加可见范围：公开、仅选课学生、仅伴学师。
5. 增加文件版本和替换逻辑。

建议涉及文件：

```text
apps/api/app/modules/files/
apps/api/app/modules/courses/
apps/web/src/pages/FilesPage.tsx
apps/web/src/pages/CourseDetailPage.tsx
```

验收标准：

- 文件能按课程和类型筛选。
- 学生只能下载自己有权限的资料。
- PDF 能在浏览器内预览。

### 3.10 安全和生产化增强

优先级：中高。

当前问题：

- 缺刷新 token、密码重置、速率限制和更细 RBAC。
- 生产密钥替换依赖人工注意。
- 上传安全只做了基本 MIME 和大小校验。

应该如何完成：

1. 增加 refresh token 或短 token + 刷新机制。
2. 增加密码重置流程。
3. 对登录、注册、上传、AI 请求增加速率限制。
4. 增加更细权限策略，例如课程拥有者、课程学生、管理员。
5. 上传文件增加扩展名校验、内容嗅探和恶意文件扫描预留。
6. 部署文档明确生产环境 secrets、HTTPS、CORS 和备份策略。

建议涉及文件：

```text
apps/api/app/modules/auth/
apps/api/app/core/security.py
apps/api/app/core/config.py
apps/api/app/modules/files/service.py
apps/api/app/modules/forum/service.py
docs/deployment.md
```

验收标准：

- 暴力登录会被限制。
- 生产环境不使用默认 `JWT_SECRET`。
- 关键操作都有明确权限检查。

### 3.11 完善测试覆盖

优先级：中高。

当前问题：

- 当前测试数量少。
- 缺课程权限、论坛权限、文件上传限制、AI 鉴权等测试。
- 没有前端组件测试和端到端测试。

应该如何完成：

1. 后端补课程模块测试：游客列表、学生加入、伴学师创建、学生不能创建。
2. 后端补论坛测试：发帖附件、评论删除权限、伴学师管理、点赞唯一性、消息提醒。
3. 后端补文件测试：类型限制、大小限制、删除权限。
4. 后端补 AI 测试：未登录拒绝、登录可访问、LLM 异常处理。
5. 前端增加 Playwright E2E：登录、课程、论坛、消息、头像上传。
6. CI 中加入构建、类型检查、后端测试和 E2E 冒烟测试。

建议涉及文件：

```text
apps/api/tests/
apps/web/
.github/workflows/ 或其他 CI 配置
```

验收标准：

- 核心权限路径都有测试。
- 提交前能自动运行构建和测试。
- 关键用户流程有 E2E 覆盖。

### 3.12 前端 UI 继续打磨

优先级：中。

当前问题：

- 主要页面已可用，但视觉一致性和响应式细节仍需继续打磨。
- 弹窗、表单、列表、空状态、错误状态还可以进一步统一。

应该如何完成：

1. 抽取统一表单弹窗和确认弹窗样式。
2. 为每个列表补充加载态、空状态、错误态。
3. 给论坛、课程、文件页面做移动端专项检查。
4. 对 AI 伴学聊天继续增强消息气泡、上下文引用、输入工具条。
5. 统一按钮、标签、头像、附件、统计卡片等组件细节。

建议涉及文件：

```text
apps/web/src/styles.css
apps/web/src/components/
apps/web/src/pages/
```

验收标准：

- 桌面和移动端没有明显重叠和溢出。
- 弹窗和列表视觉风格统一。
- 主要用户流程不需要额外说明即可完成。

## 4. 推荐开发顺序

### Phase 1: 稳定当前原型

目标：让现有功能更可靠，适合演示和提交。

任务：

1. 完善课程、论坛、文件、消息的后端测试。
2. 建立 Alembic baseline migration。
3. 修复 Docker 环境变量和部署文档中容易踩坑的地方。
4. 清理未跟踪但需要提交的前端新文件。
5. 做一次完整 Docker 重建验证。

### Phase 2: 补齐学习平台核心

目标：让它更像真实教学平台。

任务：

1. 课程章节。
2. 课件绑定课程和章节。
3. 学习事件写入。
4. 学习报告基于真实事件。
5. 论坛分页、筛选和编辑。

### Phase 3: 完成 AI 能力

目标：让 AI 伴学从占位变成可用。

任务：

1. 接入真实 LLM。
2. 课件解析。
3. chunk 切分。
4. embedding 入库。
5. pgvector 检索。
6. 引用来源展示。
7. 对话历史和反馈。

### Phase 4: 生产化

目标：从演示系统走向可部署系统。

任务：

1. 上传文件切换 MinIO。
2. WebSocket 或 SSE 实时消息。
3. 细粒度权限。
4. 安全加固。
5. CI/CD。
6. 监控、日志、备份和恢复策略。

## 5. 当前提交前检查建议

建议提交前至少执行：

```bash
npm run build --prefix apps/web
python3 -m compileall apps/api/app
APP_ENV=test apps/api/.venv/bin/python -m pytest apps/api/tests
git diff --check
```

如果使用 Docker 部署，前端源码修改后需要重建 `web`：

```bash
docker compose -f deploy/docker-compose.yml up -d --build web
```

如果后端模型、依赖或接口有修改，建议全量重建：

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```
