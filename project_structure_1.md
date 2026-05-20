# LearnMate Project Structure

本文档解释 LearnMate 当前项目结构、文件命名含义、文件作用和功能归属。文档按当前仓库实际代码编写，未跟踪的本地临时文件不纳入说明。

## 1. Overall Layout

```text
LearnMate/
├── apps/
│   ├── api/                 FastAPI 后端应用
│   └── web/                 React + TypeScript 前端应用
├── data/                    示例数据和知识库材料预留目录
├── deploy/                  Docker Compose 和部署配置
├── docs/                    设计文档
├── packages/                共享包预留目录
├── package.json             根目录 npm workspace 和快捷脚本
├── package-lock.json        npm 依赖锁定文件
├── README.md                项目总览、启动和验证入口
└── PROJECT_REVIEW.md        项目审查报告和当前能力说明
```

`apps` 表示可独立运行的应用，当前有前端 `web` 和后端 `api`。`docs` 记录设计，`deploy` 记录部署，`data` 和 `packages` 是后续扩展区域。

## 2. Root Files

| File | Meaning | Role |
|---|---|---|
| `.gitignore` | Git 忽略规则 | 排除依赖、构建产物、环境变量和上传文件等不应提交的内容。 |
| `README.md` | 项目入口文档 | 描述技术栈、功能、启动、验证和当前限制。 |
| `PROJECT_REVIEW.md` | 项目审查报告 | 汇总当前实现、验证结果、模块能力、不足和优化建议。 |
| `project_structure_1.md` | 项目结构说明 | 本文件，解释目录和关键文件职责。 |
| `package.json` | 根 npm 配置 | 使用 npm workspace 管理 `apps/web`，提供 `dev:web`、`build:web`、`preview:web` 脚本。 |
| `package-lock.json` | npm 锁文件 | 锁定前端依赖版本，保证安装结果可复现。 |

## 3. Frontend: `apps/web`

`apps/web` 是用户直接访问的 React 单页应用。它负责页面展示、用户交互、登录态本地存储、API 请求封装和 Docker 静态站点构建。

```text
apps/web/
├── Dockerfile
├── README.md
├── index.html
├── nginx.conf
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
```

| File | Meaning | Role |
|---|---|---|
| `Dockerfile` | 前端镜像构建文件 | 第一阶段运行 `npm run build`，第二阶段用 nginx 托管 `dist`。Docker 部署下不会热重载。 |
| `README.md` | 前端说明 | 记录开发、构建、页面路由、API 客户端和 Docker 注意事项。 |
| `index.html` | Vite HTML 入口 | 挂载 React 根节点并加载 `src/main.tsx`。 |
| `nginx.conf` | 前端 nginx 配置 | 支持 SPA history fallback，并把 `/api` 请求反向代理到后端容器。 |
| `package.json` | 前端依赖和脚本 | 定义 `dev`、`build`、`preview`，依赖 React、Vite、Ant Design、React Router。 |
| `tsconfig.json` | TypeScript 配置 | 控制前端 TS 编译规则。 |
| `vite.config.ts` | Vite 配置 | 配置 React 插件、开发端口 `5173` 和构建行为。 |

### 3.1 Frontend Entry And App Shell

```text
apps/web/src/
├── main.tsx
├── styles.css
├── vite-env.d.ts
├── app/
├── api/
├── components/
├── pages/
└── shared/
```

| File | Meaning | Role |
|---|---|---|
| `src/main.tsx` | 前端启动入口 | 创建 React root，挂载路由和全局 provider。 |
| `src/styles.css` | 全局样式 | 定义整体布局、导航、卡片、弹窗、论坛折叠、发帖编辑器、消息中心、AI 聊天等样式。 |
| `src/vite-env.d.ts` | Vite 类型声明 | 为 TypeScript 提供 `import.meta.env` 等 Vite 类型。 |

### 3.2 `src/app`

| File | Meaning | Role |
|---|---|---|
| `providers.tsx` | 应用级 provider | 集中包裹 Ant Design、React Router 等全局上下文。 |
| `router.tsx` | 路由表 | 使用 `React.lazy` 懒加载页面，定义 `/login`、`/courses`、`/forum`、`/forum/new`、`/assistant`、`/messages`、`/reports/me` 等路由。 |

### 3.3 `src/api`

`api` 目录按后端业务模块命名。文件名和后端模块保持对应，便于定位接口。

| File | Meaning | Role |
|---|---|---|
| `client.ts` | API 请求核心 | 读取 `VITE_API_BASE_URL`，自动附加 token，统一处理 JSON、FormData、`401`、`204` 和错误消息。 |
| `auth.ts` | 认证和用户接口 | 登录、注册、当前用户、头像上传。 |
| `courses.ts` | 课程接口 | 课程列表、课程详情、创建、编辑、删除、加入和退出课程。 |
| `forum.ts` | 论坛接口 | 帖子列表、Markdown/FormData 发帖、附件下载 URL、评论、删除评论、点赞、删除帖子。 |
| `files.ts` | 课件接口 | 文件列表、上传、下载 URL、删除。 |
| `assistant.ts` | AI 伴学接口 | 向 `/api/assistant/messages` 发送问题并接收回答。 |
| `messages.ts` | 消息接口 | 消息列表、未读数、标记已读、学生收件人、私信、公告。 |
| `reports.ts` | 报告接口 | 读取个人中心和学习报告统计。 |

### 3.4 `src/components`

`components` 放跨页面复用组件。

| File | Meaning | Role |
|---|---|---|
| `AppLayout.tsx` | 应用主布局 | 顶部品牌、导航、登录/退出、圆形头像入口、头像上传弹窗、消息未读角标和内容出口。 |
| `UserAvatar.tsx` | 用户头像组件 | 根据 `avatar_url` 显示真实头像；没有头像时显示用户名首字母。 |
| `PageHeader.tsx` | 页面标题组件 | 统一页面标题和副标题样式。 |
| `EmptyState.tsx` | 空状态组件 | 用于列表为空时的统一提示。 |

### 3.5 `src/pages`

页面文件按路由页面命名，后缀 `Page` 表示可被路由直接挂载。

| File | Route | Role |
|---|---|---|
| `LoginPage.tsx` | `/login` | 登录和注册，注册时选择学生或伴学师，处理本地 session。 |
| `DashboardPage.tsx` | `/` | 首页仪表盘，作为进入主要功能的入口。 |
| `CourseListPage.tsx` | `/courses` | 课程中心。游客浏览，学生加入/退出课程，伴学师创建/编辑/删除课程。 |
| `CourseDetailPage.tsx` | `/courses/:courseId` | 课程详情。展示课程信息、选课人数和加入状态。 |
| `ForumPage.tsx` | `/forum` | 讨论交流列表。长帖自动折叠；展开全文、点赞、评论统一在右下角；评论区在帖子内展开；伴学师可管理帖子。 |
| `ForumPostEditorPage.tsx` | `/forum/new` | 独立发帖页面。支持标题、Markdown 正文、实时预览和最多 5 个附件。 |
| `FilesPage.tsx` | `/files` | 课件资料。游客浏览下载，伴学师上传和删除自己上传的文件。 |
| `AssistantPage.tsx` | `/assistant` | AI 伴学聊天界面。登录用户可发送问题，后端当前返回占位回答。 |
| `MessagesPage.tsx` | `/messages` | 消息中心。查看点赞、评论、私信、公告；伴学师发送私信和公告。 |
| `LearningReportPage.tsx` | `/reports/me` | 个人中心/学习报告。展示课程、互动、估算投入、进度和建议。 |

### 3.6 `src/shared`

| File | Meaning | Role |
|---|---|---|
| `shared/types/user.ts` | 用户类型 | 前端共享的用户数据结构。 |
| `shared/utils/currentUser.ts` | 登录态工具 | 读写 token 和当前用户，提供更新头像后的本地用户同步。 |
| `shared/utils/useCurrentUser.ts` | 当前用户 Hook | 响应式读取本地用户信息，供布局和页面判断角色。 |
| `shared/utils/formatDate.ts` | 日期格式工具 | 统一格式化后端返回时间。 |
| `shared/utils/markdown.ts` | Markdown 渲染工具 | 支持标题、列表、加粗、斜体、行内代码，并先转义 HTML，供发帖预览和论坛展示使用。 |

## 4. Backend: `apps/api`

`apps/api` 是 FastAPI 后端应用。目录按领域模块拆分，每个模块通常包含 `api.py`、`schemas.py`、`models.py`、`repository.py`、`service.py`。

```text
apps/api/
├── Dockerfile
├── README.md
├── pyproject.toml
├── requirements.txt
├── app/
├── storage/
└── tests/
```

| File | Meaning | Role |
|---|---|---|
| `Dockerfile` | 后端镜像构建文件 | 安装 Python 依赖并启动 FastAPI 服务。 |
| `README.md` | 后端说明 | 记录开发启动、配置、模块、接口和测试。 |
| `requirements.txt` | Python 依赖 | FastAPI、SQLAlchemy、Pydantic、JWT、pytest 等依赖。 |
| `pyproject.toml` | Python 项目配置 | 保存项目元信息和工具配置预留。 |
| `storage/uploads/.gitkeep` | 上传目录占位 | 保留本地上传目录结构；真实上传文件不应提交。 |

### 4.1 Backend Naming Convention

| File Name | Meaning |
|---|---|
| `api.py` | HTTP 路由层，声明 URL、请求依赖、响应模型和状态码。 |
| `schemas.py` | Pydantic 请求/响应模型，定义接口数据形状。 |
| `models.py` | SQLAlchemy ORM 模型，定义数据库表。 |
| `repository.py` | 数据访问层，封装查询、创建、更新、删除。 |
| `service.py` | 业务逻辑层，处理权限、流程、校验、跨模块调用。 |
| `dependencies.py` | FastAPI 依赖函数，如认证和角色解析。 |
| `__init__.py` | Python 包标记，也方便模块导入。 |

### 4.2 `app/main.py`

FastAPI 应用入口。它创建应用、配置 CORS、注册静态文件和所有业务路由，并在 lifespan 中初始化数据库。健康检查接口是 `/api/health`。

### 4.3 `app/core`

| File | Meaning | Role |
|---|---|---|
| `config.py` | 配置中心 | 从 `.env` 读取数据库、Redis、JWT、CORS、MinIO、上传限制和大模型配置。 |
| `database.py` | 数据库连接 | 创建 SQLAlchemy `engine`、`SessionLocal`、`Base` 和 `get_db` 依赖。 |
| `init_db.py` | 数据库初始化 | 导入所有 ORM 模型并执行 `create_all()`；开发期用补丁 SQL 补齐头像、课程、论坛附件、消息等字段/表。 |
| `security.py` | 安全工具 | 密码哈希、密码校验、JWT 创建和解析。 |

### 4.4 `app/common`

| File | Meaning | Role |
|---|---|---|
| `exceptions.py` | 通用异常 | 预留统一异常类型。 |
| `pagination.py` | 分页结构 | 预留分页参数或响应结构。当前论坛和课程尚未真正分页。 |
| `responses.py` | 通用响应 | 预留统一响应封装。 |

### 4.5 `app/infrastructure`

基础设施适配层用于隔离外部服务。当前多数是预留或占位。

| File | Meaning | Role |
|---|---|---|
| `llm_client.py` | 大模型客户端 | 当前返回占位回答，后续接 OpenAI-compatible 或其他 LLM。 |
| `vector_store.py` | 向量检索 | 当前搜索占位，后续接 pgvector 和 embedding 检索。 |
| `object_storage.py` | 对象存储 | MinIO 接入预留。当前上传仍写本地磁盘。 |
| `redis.py` | Redis 连接 | Redis 基础设施预留。 |

### 4.6 Auth Module: `app/modules/auth`

认证模块负责账号、角色、token 和当前用户依赖。

| File | Role |
|---|---|
| `models.py` | 定义 `users` 表：用户名、密码哈希、角色、头像地址。 |
| `schemas.py` | 登录、注册、token、用户响应模型。 |
| `repository.py` | 根据用户名或 ID 查询用户、创建用户。 |
| `service.py` | 注册校验、用户名规范化、密码验证、JWT 返回。 |
| `dependencies.py` | `get_current_user`、`get_optional_current_user` 等鉴权依赖。 |
| `api.py` | `/api/auth/register` 和 `/api/auth/login`。 |

相关功能：登录注册、学生/伴学师身份、游客可选鉴权、前端自动携带 token。

### 4.7 Users Module: `app/modules/users`

用户模块处理当前用户资料和头像上传。

| File | Role |
|---|---|
| `api.py` | `/api/users/me` 和 `/api/users/me/avatar`。 |
| `service.py` | 头像类型/大小校验、头像文件保存、用户 `avatar_url` 更新。 |

相关功能：顶部圆形头像、自定义上传头像、评论/帖子作者头像展示。

### 4.8 Courses Module: `app/modules/courses`

课程模块负责课程和选课。

| File | Role |
|---|---|
| `models.py` | 定义 `courses` 和 `course_enrollments` 表。 |
| `schemas.py` | 课程创建、更新、响应模型，包含 `enrollment_count` 和 `joined_by_me`。 |
| `repository.py` | 课程 CRUD、选课关系查询和计数。 |
| `service.py` | 伴学师创建/编辑/删除课程，学生加入/退出课程，权限校验。 |
| `api.py` | `/api/courses` 及课程详情、选课接口。 |

相关功能：课程中心、课程详情、学生加入退出、伴学师课程管理。

### 4.9 Forum Module: `app/modules/forum`

论坛模块负责帖子、评论、点赞和附件。

| File | Role |
|---|---|
| `models.py` | 定义 `forum_posts`、`forum_comments`、`forum_likes` 表。帖子用 `attachments` 文本字段保存附件 JSON。 |
| `schemas.py` | 帖子、评论、附件、点赞响应模型。 |
| `repository.py` | 帖子列表、评论列表、点赞切换、统计、头像查询、删除。 |
| `service.py` | 发帖附件保存、权限校验、评论删除规则、点赞/评论消息提醒、附件下载路径校验。 |
| `api.py` | `/api/forum/posts`、评论、点赞、删除和附件下载接口。 |

相关功能：Markdown 发帖、最多 5 个附件、帖子列表自动折叠、右下角互动按钮、评论区内联展开、学生删除自己的评论、伴学师删除帖子和评论、点赞/评论提醒。

### 4.10 Messages Module: `app/modules/messages`

消息模块负责通知、私信和公告。

| File | Role |
|---|---|
| `models.py` | 定义 `user_messages` 表：接收者、发送者、类型、标题、内容、来源、已读状态。 |
| `schemas.py` | 消息响应、未读数、学生收件人、私信、公告请求/响应模型。 |
| `repository.py` | 消息列表、未读计数、标记已读、批量创建、学生列表查询。 |
| `service.py` | 伴学师私信和公告权限；点赞/评论生成提醒；自己给自己操作不提醒。 |
| `api.py` | `/api/messages`、未读数、标记已读、私信、公告。 |

相关功能：顶部消息未读角标、消息中心、点赞提醒、评论提醒、伴学师发私信和公告。

### 4.11 Files Module: `app/modules/files`

课件模块负责文件上传、下载和删除。

| File | Role |
|---|---|
| `models.py` | 定义 `file_assets` 表，保存原始名、存储名、MIME、大小、上传者。 |
| `schemas.py` | 文件响应模型。 |
| `repository.py` | 文件元数据 CRUD。 |
| `service.py` | 上传大小/类型校验、本地保存、下载路径、删除权限。 |
| `api.py` | `/api/files`、上传、下载、删除。 |

相关功能：课件资料页、游客下载、伴学师上传和删除自己上传的课件。

### 4.12 Assistant Module: `app/modules/assistant`

AI 伴学模块已经打通接口边界，但核心 AI 能力仍是占位。

| File | Role |
|---|---|
| `models.py` | 定义 `assistant_sessions` 预留表。 |
| `schemas.py` | 提问请求、回答、引用来源响应模型。 |
| `api.py` | `/api/assistant/messages`，要求登录用户。 |
| `chat_service.py` | 编排检索、prompt 构建和 LLM 调用。 |
| `retrieval_service.py` | 检索服务入口，当前调用占位向量库。 |
| `prompt_builder.py` | 把问题和资料片段组装成 prompt。 |
| `knowledge_ingestion.py` | 知识入库流程预留。 |
| `repository.py` | 会话/消息持久化预留。 |

相关功能：AI 伴学聊天页面、后端鉴权和占位回答。后续要接真实 LLM、embedding、pgvector 和引用来源。

### 4.13 Reports Module: `app/modules/reports`

报告模块提供个人中心统计。

| File | Role |
|---|---|
| `models.py` | 定义 `learning_reports` 预留表。 |
| `schemas.py` | 个人报告响应结构。 |
| `repository.py` | 查询课程、选课和论坛互动统计。 |
| `service.py` | 生成课程数、互动数、估算学习投入、进度、学习轨迹和建议。 |
| `api.py` | `/api/reports/me`。 |

相关功能：个人中心/学习报告页。

### 4.14 Learning Records Module: `app/modules/learning_records`

学习记录模块是学习数据闭环的预留模块。

| File | Role |
|---|---|
| `models.py` | 定义 `learning_events` 表。 |
| `schemas.py` | 学习事件结构预留。 |
| `repository.py` | 学习事件数据访问预留。 |
| `service.py` | 学习事件业务逻辑预留。 |
| `api.py` | 学习记录接口预留。 |

当前课程、论坛、AI 行为还没有完整写入该模块。

### 4.15 Backend Tests: `apps/api/tests`

| File | Role |
|---|---|
| `test_health.py` | 测试 `/api/health`。 |
| `test_auth_validation.py` | 测试注册用户名规则。 |
| `test_users_avatar.py` | 测试头像上传鉴权和服务逻辑。 |
| `test_messages.py` | 测试消息接口鉴权、未读数和学生发私信权限。 |
| `test_reports.py` | 测试个人报告鉴权和响应结构。 |

测试运行命令：

```bash
APP_ENV=test apps/api/.venv/bin/python -m pytest apps/api/tests
```

## 5. Deployment: `deploy`

```text
deploy/
├── README.md
├── docker-compose.yml
├── env.example
└── nginx/
    └── learnmate.conf
```

| File | Meaning | Role |
|---|---|---|
| `docker-compose.yml` | 本地容器编排 | 启动 `postgres`、`redis`、`minio`、`api`、`web`。前端映射 `5173:80`，后端映射 `8000:8000`。 |
| `env.example` | Docker 环境变量模板 | 使用容器服务名 `postgres`、`redis`、`minio`，适合复制到 `apps/api/.env`。 |
| `README.md` | 部署说明 | 记录初始化 `.env`、启动基础服务、启动全部服务、只重建前端。 |
| `nginx/learnmate.conf` | 独立 nginx 配置预留 | 面向服务器部署时的反向代理配置参考。 |

Docker 部署下 `web` 是 nginx 静态站点，不是 Vite 开发服务器。修改前端源码后需要：

```bash
docker compose -f deploy/docker-compose.yml up -d --build web
```

## 6. Data: `data`

| File | Role |
|---|---|
| `data/knowledge-base/README.md` | RAG 知识库材料目录说明，后续可放课程资料和切片来源。 |
| `data/seed/README.md` | 种子数据目录说明，后续可放初始化课程、用户或示例数据。 |

## 7. Shared Package: `packages/shared-types`

当前只有 `README.md`。该目录用于后续沉淀前后端共享类型，例如用户角色、课程状态、消息类型等。当前实际共享类型还分别散落在前端 TypeScript 和后端 Pydantic schema 中。

## 8. Docs

| File | Role |
|---|---|
| `docs/README.md` | 设计文档目录说明。 |
| `docs/api-design.md` | 接口设计，按 Auth、Users、Courses、Forum、Messages、Files、Assistant、Reports 分组。 |
| `docs/database-design.md` | 当前数据库表、字段、约束和后续表设计建议。 |
| `docs/ai-assistant-design.md` | AI 伴学 RAG 目标、当前状态、运行流程和下一步。 |
| `docs/deployment.md` | Docker Compose 部署、环境变量和当前限制。 |

## 9. Runtime Flow

### 9.1 Login

```text
LoginPage.tsx
  -> api/auth.ts
  -> POST /api/auth/login
  -> auth/api.py
  -> AuthService
  -> UserRepository
  -> JWT + UserResponse
  -> currentUser.ts 保存 token 和用户
```

### 9.2 Forum Post Creation

```text
ForumPostEditorPage.tsx
  -> renderMarkdown() 实时预览
  -> api/forum.ts createPost(FormData)
  -> POST /api/forum/posts
  -> forum/api.py
  -> ForumService._store_attachments()
  -> ForumRepository.create_post()
  -> ForumPostResponse
```

### 9.3 Forum Interaction And Notifications

```text
ForumPage.tsx
  -> togglePostLike() / createComment()
  -> forum/service.py
  -> ForumRepository 更新点赞或评论
  -> MessageService.notify_post_liked/commented()
  -> user_messages 表
  -> AppLayout 每 30 秒刷新未读数
```

### 9.4 Avatar Upload

```text
AppLayout.tsx
  -> uploadMyAvatar(file)
  -> POST /api/users/me/avatar
  -> users/service.py 校验和保存图片
  -> 更新 users.avatar_url
  -> updateStoredCurrentUser()
  -> UserAvatar 显示新头像
```

### 9.5 AI Assistant

```text
AssistantPage.tsx
  -> api/assistant.ts
  -> POST /api/assistant/messages
  -> AssistantChatService.answer()
  -> RetrievalService.retrieve()
  -> VectorStore.search() 占位
  -> build_prompt()
  -> LLMClient.chat() 占位
  -> 返回 answer 和 citations
```

## 10. Current Important Limitations

- AI 伴学接口已打通，但真实大模型、embedding、pgvector 检索和引用来源仍未实现。
- MinIO 已在配置和 Compose 中预留，但课件、头像和论坛附件当前仍写后端本地磁盘。
- 数据库迁移尚未正式 Alembic 化，当前依赖 `create_all()` 和开发期补丁 SQL。
- 课程尚无章节体系，课件没有绑定到具体课程。
- 论坛尚无分页、搜索、课程筛选、编辑帖子、软删除、内容审核和举报。
- 学习记录模块已有表和目录，但业务行为还没有完整写入学习事件。
