# LearnMate Completion Checklist

整理日期：2026-05-25
项目阶段：可演示的进阶原型，课程、互动、资料、智能检索问答、学习记录、伴学师教学看板和儿童化展示 UI 已经形成闭环；距离生产级系统仍需要安全、测试、部署和智能能力增强。

本文档用于回答三个问题：

1. 当前已经完成了什么。
2. 每个已完成功能由哪些模块和文件实现。
3. 还没有完成什么，以及下一步应该如何完成。

## 1. 总体状态

| Area | Status | Summary |
|---|---|---|
| 前端应用 | 已完成核心页面 | React + TypeScript + Vite 单页应用已可运行，页面路由、顶部导航、登录态、头像、消息红点和主要业务页面已实现。 |
| 后端应用 | 已完成核心 API | FastAPI + SQLAlchemy 后端已实现认证、课程、论坛、文件、消息、报告和智能伴学接口边界。 |
| 课程业务 | 基本完成 | 游客浏览、独立创建课程、伴学师建课/改课/删课、草稿仅创建者可见、学生加入/退出课程和学生名单管理已实现。 |
| 论坛业务 | 基本完成 | Markdown 发帖、附件、长帖折叠、评论、点赞、评论删除、伴学师管理、消息提醒已实现；帖子列表已取消附带标签展示。 |
| 文件业务 | 基本完成 | 课件上传、列表、下载、删除、课程/章节绑定、知识库切片和本地/MinIO 课件存储已实现；头像和论坛附件仍以本地目录为主。 |
| 消息业务 | 基本完成 | 点赞提醒、评论提醒、私信、公告、未读数和已读状态已实现。 |
| 智能伴学 | 基本完成可演示 | 已支持课程资料检索、引用来源、会话落库、本地检索式回答和 OpenAI 兼容大模型配置；流式输出、安全限制和 pgvector 原生索引仍需增强。 |
| 个人中心 | 基本完成可演示 | 学生学习报告和伴学师教学看板已按角色区分；更精细的课程进度、学生画像和教学数据仍可继续完善。 |
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
- 顶部导航包含课程中心、讨论交流、智能伴学、消息中心、个人中心。
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

- 访问 `/courses`、`/courses/new`、`/forum`、`/forum/new`、`/files`、`/assistant`、`/messages`、`/reports/me` 能进入对应页面。
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
- 伴学师可通过独立创建页创建课程，并编辑、删除自己创建的课程。
- 草稿课程仅创建它的伴学师可见，学生和游客无法看到草稿课程、章节、课件和讨论。
- 学生可加入和退出课程。
- 课程作者可查看学生名单，并从课程中移除学生。
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
| 创建课程页 | `apps/web/src/pages/CourseCreatePage.tsx` |
| 课程详情页 | `apps/web/src/pages/CourseDetailPage.tsx` |

验收方式：

- 游客能看到课程列表。
- 学生看到加入/退出课程操作。
- 伴学师看到创建、编辑、删除课程操作。
- 伴学师从 `/courses/new` 创建课程，创建后进入课程详情继续维护章节、课件和学生名单。
- 草稿课程只在创建者的课程列表和详情中出现。
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
- 帖子列表不再展示附带标签，减少每条帖子内部的视觉噪音。
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
- 课件可绑定课程和章节。
- 课件可使用本地存储或 MinIO 存储。
- 文本类、Markdown、DOCX 和 PDF 课件会抽取文本并写入知识库 chunk。

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
| 对象存储适配 | `apps/api/app/infrastructure/object_storage.py` |
| 知识库入库 | `apps/api/app/modules/assistant/knowledge_ingestion.py` |

验收方式：

- 游客能看到课件列表并下载。
- 学生不能上传课件。
- 伴学师能上传课件。
- 上传不支持类型或超大文件会失败。

### 2.9 智能伴学页面和接口

状态：基本完成可演示。

已实现内容：

- 前端有智能伴学聊天页面。
- 登录用户可选择课程资料并发送问题。
- 游客看到登录提示。
- 后端有 `/api/assistant/messages` 接口。
- 后端已经拆出检索、Prompt、LLM 客户端等边界。
- 课件上传后会抽取文本、切片并写入 `knowledge_chunks`。
- 检索层支持本地哈希 embedding 余弦相似度 + 关键词混合检索。
- 回答会返回引用来源 `citations`。
- 配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 后可调用 OpenAI 兼容大模型。
- 未配置外部模型时使用本地检索式回答，适合课堂演示和离线展示。
- 智能伴学问答会写入会话、消息和学习事件。

实现位置：

| Part | Files |
|---|---|
| 前端 AI 页面 | `apps/web/src/pages/AssistantPage.tsx` |
| 前端 AI API | `apps/web/src/api/assistant.ts` |
| 后端 AI 接口 | `apps/api/app/modules/assistant/api.py` |
| 对话编排服务 | `apps/api/app/modules/assistant/chat_service.py` |
| 检索服务 | `apps/api/app/modules/assistant/retrieval_service.py` |
| Prompt 构造 | `apps/api/app/modules/assistant/prompt_builder.py` |
| 轻量向量检索 | `apps/api/app/infrastructure/vector_store.py` |
| LLM 客户端 | `apps/api/app/infrastructure/llm_client.py` |
| 知识库入库 | `apps/api/app/modules/assistant/knowledge_ingestion.py` |

当前限制：

- 没有流式输出。
- 没有前端会话列表和历史消息管理。
- 未接外部 embedding 模型和 pgvector 原生向量索引。
- 未接图片 OCR。
- 生产环境还需要输入长度限制、频率限制、输出安全检查和审计。

### 2.10 个人中心、学习报告和教学看板

状态：轻量完成。

已实现内容：

- 登录用户可访问个人中心。
- 学生看到学习报告，包含课程数量、讨论互动、估算学习投入、进度、学习轨迹和建议。
- 伴学师看到教学看板，包含建课数量、选课学生数、章节数、课件数、课程概览、教学动态和教学建议。
- 统计当前基于课程、学生名单、章节、论坛、智能伴学问答、资料上传和学习事件。

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
- 学生页面能展示课程、讨论和建议统计。
- 伴学师页面能展示课程建设、学生参与、章节资料、课程概览和教学建议。

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
- 有智能伴学接口鉴权、会话和引用结构测试。
- 有课程章节和学习事件测试。

实现位置：

| Part | Files |
|---|---|
| 健康检查测试 | `apps/api/tests/test_health.py` |
| 认证校验测试 | `apps/api/tests/test_auth_validation.py` |
| 头像测试 | `apps/api/tests/test_users_avatar.py` |
| 消息测试 | `apps/api/tests/test_messages.py` |
| 报告测试 | `apps/api/tests/test_reports.py` |
| AI 测试 | `apps/api/tests/test_assistant.py` |
| 章节测试 | `apps/api/tests/test_course_chapters.py` |
| 学习事件测试 | `apps/api/tests/test_learning_records.py` |

验收方式：

```bash
APP_ENV=test apps/api/.venv/bin/python -m pytest apps/api/tests
```

## 3. 待完成清单

### 3.1 增强真实 AI 大模型接入和使用限制

优先级：高。

当前问题：

- `LLMClient.chat()` 已支持 OpenAI 兼容接口和本地检索式兜底，但生产级限制还不完整。
- 目前缺少更严格的输入长度限制、单用户频率限制、模型输出 token 上限和内容安全边界。
- 模型失败、超时、供应商限流等场景还可以继续细化用户提示和降级策略。

应该如何完成：

1. 在 `apps/api/app/modules/assistant/api.py` 和 `schemas.py` 中收紧输入长度、空白内容和课程权限校验。
2. 在 `apps/api/app/infrastructure/llm_client.py` 中完善 timeout、重试、错误分类和响应长度控制。
3. 在 `apps/api/app/core/config.py` 中增加模型请求上限、默认 `max_tokens`、温度和供应商配置说明。
4. 增加基于 Redis 或数据库的 AI 请求频率限制。
5. 增加拒答边界、敏感信息脱敏、日志审计和异常降级策略。
6. 为模型成功、失败、超时、限流和本地兜底补充测试。

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

- 配置真实 API Key 后，智能伴学能返回真实模型回答。
- 模型服务不可用时，系统能稳定降级或显示友好错误。
- 后端不会把 API Key 输出到日志或响应中。
- 短时间高频请求会被限制。
- 单次请求和回答长度都在可控范围内。

### 3.2 升级 RAG 知识库检索

优先级：高。

当前问题：

- 目前已有课件解析、切片、`knowledge_chunks` 入库、轻量 embedding 和引用来源。
- 当前 embedding 为本地哈希向量，适合演示，但语义理解能力有限。
- PostgreSQL 中的 `embedding` 当前以 JSON 形式保存，还没有使用 pgvector 原生向量列和索引。
- 图片 OCR、扫描版 PDF 和更复杂的版面解析尚未接入。

应该如何完成：

1. 接入外部 embedding 模型，替换本地哈希向量。
2. 使用 Alembic 增加 pgvector 原生向量列和索引。
3. 将已有 `knowledge_chunks.embedding` 数据迁移到新的向量列。
4. 优化 `VectorStore.search()` 的相似度排序、关键词混合权重和课程过滤。
5. 为 PDF 页码、DOCX 段落和章节信息补充更清晰的 citation 元数据。
6. 增加 OCR/版面解析能力，把扫描件和图片课件纳入知识库。
7. 增加知识库重建脚本，支持课件更新后重新切片和重新生成向量。

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
- 相似度检索可使用 pgvector 索引，真实课程资料增多后仍能保持响应速度。

### 3.3 完善 Alembic 数据库迁移流程

优先级：高。

当前问题：

- 项目已提供 Alembic 配置和首版初始 schema 迁移。
- 开发环境启动仍保留 `Base.metadata.create_all()` 和 `init_db.py` 中的兼容补丁 SQL。
- 还需要完成真实 PostgreSQL 在线迁移演练、回滚流程和后续变更规范。

应该如何完成：

1. 在真实 PostgreSQL 环境执行 `alembic upgrade head` 在线验证。
2. 将后续 schema 变更全部固化为新的 migration。
3. 逐步移除生产启动对 `init_db.py` 补丁 SQL 的依赖。
4. 为回滚、备份和失败恢复补充部署文档。
5. 测试环境保留轻量初始化方式，或单独使用测试迁移。
6. CI 中增加 migration 生成和离线 SQL 检查。

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

### 3.4 统一对象存储策略

优先级：高。

当前问题：

- 课件资料已经支持 `STORAGE_BACKEND=local|minio`。
- 头像和论坛附件仍写在后端本地目录。
- 多实例部署、容器重建和备份恢复时，本地附件仍容易不一致。

应该如何完成：

1. 扩展 `object_storage.py` 的统一接口，覆盖头像和论坛附件。
2. 改造 `users/service.py`、`forum/service.py` 使用对象存储。
3. 为头像和论坛附件保存对象 key、原始文件名、MIME、大小和 bucket。
4. 对私有文件使用后端代理下载或短期签名 URL。
5. 增加迁移脚本，把已有本地头像和论坛附件迁移到 MinIO。
6. 部署文档中明确本地存储目录挂载和 MinIO bucket 备份策略。

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
- 重建 API 容器后课件、头像和论坛附件仍可下载或展示。

### 3.5 完善学习记录闭环

优先级：高。

当前问题：

- `learning_records` 模块已经能记录选课、章节、上传、论坛互动和 AI 提问等事件。
- 课程学习进度仍主要是估算，缺少章节完成、资料阅读时长、测验结果等更细粒度事件。
- 课件下载、在线预览停留时间和自主测试结果仍可继续补充。

应该如何完成：

1. 补充 `file_downloaded`、`chapter_completed`、`quiz_finished`、`material_viewed` 等事件。
2. 为事件增加更稳定的对象类型、对象 ID、元数据规范。
3. 改造 `reports/service.py`，基于更细粒度事件计算投入、进度和建议。
4. 前端报告页展示章节完成度、最近学习资料和自主测试反馈。
5. 增加伴学师视角的学生学习概览。

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

### 3.6 增强课程章节、任务和进度

优先级：中高。

当前问题：

- 课程章节和课件绑定已经实现。
- 还没有章节完成状态、课后任务、测验和作业提交。
- 学生端仍可继续增强“我的课程”和学习路径视图。

应该如何完成：

1. 为章节增加完成状态和学习进度。
2. 增加课后任务、测验或作业提交结构。
3. 伴学师可查看每个章节的学生完成情况。
4. 学生在课程详情页看到下一步学习建议。
5. 智能伴学检索继续按课程/章节资料过滤知识库。

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
- 学生能标记或自动记录章节学习进度。

### 3.7 完善论坛高级能力

优先级：中。

当前问题：

- 已有分页、关键词搜索和按课程筛选。
- 帖子不能编辑。
- 删除是硬删除。
- 没有举报、审核和内容安全机制。

应该如何完成：

1. 新增帖子编辑接口，只允许作者或伴学师按规则操作。
2. 将硬删除改为软删除字段，例如 `deleted_at`、`deleted_by`。
3. 新增举报表和审核状态。
4. 增加内容安全检查和违规词提示。
5. 前端论坛页增加编辑入口、举报入口和审核状态提示。

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
- 缺课程权限、论坛权限、文件上传限制、智能伴学鉴权、草稿可见性和教学看板聚合等测试。
- 没有前端组件测试和端到端测试。

应该如何完成：

1. 后端补课程模块测试：游客列表、学生加入、伴学师创建、学生不能创建。
2. 后端补论坛测试：发帖附件、评论删除权限、伴学师管理、点赞唯一性、消息提醒。
3. 后端补文件测试：类型限制、大小限制、删除权限。
4. 后端补智能伴学测试：未登录拒绝、登录可访问、LLM 异常处理。
5. 后端补草稿课程可见性、学生名单管理和伴学师报告聚合测试。
6. 前端增加 Playwright E2E：登录、课程、论坛、消息、头像上传、创建课程、学生名单和教学看板。
7. CI 中加入构建、类型检查、后端测试和 E2E 冒烟测试。

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
4. 对智能伴学聊天继续增强消息气泡、上下文引用、输入工具条。
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
2. 在真实 PostgreSQL 上验证 Alembic 初始迁移和后续迁移流程。
3. 修复 Docker 环境变量和部署文档中容易踩坑的地方。
4. 整理演示数据脚本、截图账号和展示文案。
5. 做一次完整 Docker 重建验证。

### Phase 2: 补齐学习平台核心

目标：让它更像真实教学平台。

任务：

1. 章节学习进度。
2. 课后任务、测验和自主反馈。
3. 更细粒度学习事件。
4. 伴学师课程学生进度、待回复讨论和课程健康度。
5. 论坛帖子编辑、举报和审核流程。

### Phase 3: 增强 AI 能力

目标：让智能伴学从可演示走向更稳定、更安全、更懂课程资料。

任务：

1. 外部 embedding 模型。
2. pgvector 原生向量列和索引。
3. SSE 流式输出。
4. 会话列表、历史消息和多轮上下文预算。
5. 回答反馈、评测集和人工复核。
6. 输入限流、输出安全检查和审计。
7. OCR 与复杂课件解析。

### Phase 4: 生产化

目标：从演示系统走向可部署系统。

任务：

1. 头像和论坛附件统一切换对象存储。
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
