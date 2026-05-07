# 智能伴学系统第一版技术栈详解

本文档详细说明 `guochuang` 智能伴学系统第一版推荐技术栈：

```text
React + TypeScript + Vite
FastAPI
PostgreSQL + pgvector
Redis
MinIO
Docker Compose
```

这套组合适合第一版系统，因为它既能较快做出登录、课程、论坛、AI 问答、学习报告等核心功能，也方便以后扩展课程知识库、个性化学习推荐、教师数据看板等智能化能力。

## 1. 整体结构是什么样的

第一版系统可以理解为六个核心部分：

```text
浏览器
  |
  v
React 前端
  |
  | HTTP / SSE
  v
FastAPI 后端
  |
  +--> PostgreSQL：业务数据
  +--> pgvector：知识库向量检索
  +--> Redis：缓存、限流、后台任务
  +--> MinIO：课件、头像、附件文件
  +--> 大模型 API：AI 助教回答
```

项目目录建议：

```text
guochuang/
├── README.md
├── ARCHITECTURE.md
├── TECH_STACK_V1.md
├── docs/
│   ├── api-design.md
│   ├── database-design.md
│   ├── ai-assistant-design.md
│   └── deployment.md
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── pages/
│   │   │   ├── features/
│   │   │   ├── components/
│   │   │   ├── api/
│   │   │   ├── shared/
│   │   │   └── main.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── core/
│       │   ├── modules/
│       │   ├── infrastructure/
│       │   └── common/
│       ├── migrations/
│       └── pyproject.toml
├── packages/
│   └── shared-types/
├── deploy/
│   ├── docker-compose.yml
│   ├── nginx/
│   └── env.example
└── data/
    └── knowledge-base/
```

## 2. React 是什么

React 是前端 UI 库，用来开发用户能看到和操作的网页界面。

在本项目中，React 负责：

- 登录页面。
- 学生首页。
- 课程列表和课程详情。
- 选课操作。
- 论坛发帖和回帖页面。
- AI 助教聊天页面。
- 学习报告页面。
- 教师课程管理页面。
- 管理员后台页面。

React 不是数据库，也不是后端服务。它主要运行在用户浏览器里，负责把数据展示成界面，并把用户操作发送给后端。

### 2.1 React 前端结构

建议结构：

```text
apps/web/src/
├── main.tsx
├── app/
│   ├── router.tsx
│   ├── providers.tsx
│   └── layout.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── CourseListPage.tsx
│   ├── CourseDetailPage.tsx
│   ├── ForumPage.tsx
│   ├── AssistantPage.tsx
│   └── LearningReportPage.tsx
├── features/
│   ├── auth/
│   ├── courses/
│   ├── forum/
│   ├── assistant/
│   └── reports/
├── components/
│   ├── AppLayout.tsx
│   ├── UserMenu.tsx
│   ├── CourseCard.tsx
│   ├── MarkdownRenderer.tsx
│   └── EmptyState.tsx
├── api/
│   ├── client.ts
│   ├── auth.ts
│   ├── courses.ts
│   ├── forum.ts
│   ├── assistant.ts
│   └── reports.ts
└── shared/
    ├── types/
    ├── utils/
    ├── constants/
    └── hooks/
```

### 2.2 React 的特点

- 组件化：页面可以拆成按钮、表单、卡片、列表、聊天框等组件。
- 状态驱动：数据变了，界面自动重新渲染。
- 生态成熟：路由、请求、表单、图表、Markdown 渲染都有成熟库。
- 适合复杂交互：AI 聊天、课程管理、论坛互动、报告图表都适合用 React 做。
- 适合团队协作：不同同学可以分别负责不同页面或功能模块。

### 2.3 React 在项目里的例子

学生点击“选课”：

```text
CourseDetailPage.tsx
  |
  v
features/courses/enroll-button.tsx
  |
  v
api/courses.ts
  |
  v
POST /api/courses/{course_id}/enroll
```

前端只负责触发请求和展示结果，真正判断课程是否满员、学生是否已经选过课，应由后端完成。

## 3. TypeScript 是什么

TypeScript 是 JavaScript 的增强版，增加了类型系统。

在本项目中，TypeScript 负责让前端代码更可靠。例如课程数据可以定义成：

```ts
export type Course = {
  id: string;
  title: string;
  description: string;
  teacherName: string;
  capacity: number;
  enrolledCount: number;
  status: "draft" | "published" | "archived";
};
```

这样写的好处是：

- 写代码时能提前发现字段拼错。
- 接口返回数据结构更清楚。
- 组件传参更安全。
- 项目变大后更容易维护。

对团队项目来说，React + TypeScript 比纯 React + JavaScript 更适合长期开发。

## 4. Vite 是什么

Vite 是前端构建工具。

它负责：

- 启动前端开发服务器。
- 编译 React 和 TypeScript。
- 处理 CSS、图片、字体等资源。
- 打包生成生产环境静态文件。

在开发时：

```text
npm run dev
```

Vite 会启动本地前端服务，例如：

```text
http://localhost:5173
```

打包时：

```text
npm run build
```

Vite 会生成：

```text
apps/web/dist/
```

这个目录可以交给 Nginx 部署。

### 4.1 Vite 的特点

- 启动快。
- 热更新快。
- 配置简单。
- 和 React、TypeScript 配合成熟。
- 适合从零开始搭建前端项目。

## 5. FastAPI 是什么

FastAPI 是 Python 后端 Web 框架，用来开发 API 服务。

在本项目中，FastAPI 负责：

- 登录、注册、鉴权。
- 用户信息接口。
- 课程增删改查。
- 选课和退课。
- 论坛发帖和回帖。
- AI 助教问答接口。
- 学习记录写入。
- 学习报告生成。
- 文件上传入口。

浏览器中的 React 前端不会直接操作数据库，而是通过 FastAPI 提供的接口访问系统能力。

### 5.1 FastAPI 后端结构

建议结构：

```text
apps/api/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── logging.py
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── api.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   ├── models.py
│   │   │   └── repository.py
│   │   ├── users/
│   │   ├── courses/
│   │   ├── forum/
│   │   ├── assistant/
│   │   ├── learning_records/
│   │   └── reports/
│   ├── infrastructure/
│   │   ├── redis.py
│   │   ├── object_storage.py
│   │   ├── vector_store.py
│   │   └── llm_client.py
│   └── common/
│       ├── exceptions.py
│       ├── responses.py
│       └── pagination.py
├── migrations/
├── tests/
├── pyproject.toml
└── alembic.ini
```

### 5.2 FastAPI 的特点

- 适合写 REST API。
- 类型清晰，配合 Pydantic 做参数校验。
- 自动生成接口文档，方便前后端联调。
- Python 生态适合 AI、数据分析、文本处理。
- 支持异步，适合处理外部 API 调用。
- 适合把大模型、向量检索、课件解析等能力整合进平台。

### 5.3 FastAPI 在项目里的例子

学生选课流程：

```text
POST /api/courses/{course_id}/enroll
  |
  v
courses/api.py 接收请求
  |
  v
courses/service.py 判断业务规则
  |
  v
courses/repository.py 写入数据库
  |
  v
返回选课结果
```

业务规则不要写在前端，因为前端代码可以被绕过。选课容量、权限判断、重复选课检查都应该由后端负责。

## 6. PostgreSQL 是什么

PostgreSQL 是关系型数据库，用来保存结构化业务数据。

在本项目中，PostgreSQL 保存：

- 用户账号。
- 学生、教师、管理员角色。
- 课程信息。
- 章节信息。
- 选课记录。
- 论坛帖子。
- 回帖。
- AI 对话记录。
- 学习行为。
- 学习报告。

### 6.1 数据库结构示例

```text
users
courses
course_chapters
course_materials
enrollments
forum_posts
forum_replies
assistant_sessions
assistant_messages
learning_events
learning_progress
learning_reports
```

### 6.2 PostgreSQL 的特点

- 稳定可靠。
- 支持复杂查询。
- 支持事务，适合选课这种需要一致性的场景。
- 支持 JSON 字段，可以保存灵活结构的数据。
- 可以通过 pgvector 扩展支持向量检索。

### 6.3 PostgreSQL 在项目里的例子

选课必须用数据库事务保障一致性：

```text
查询课程容量
查询当前选课人数
检查学生是否已选
插入选课记录
提交事务
```

如果两个学生同时抢最后一个名额，数据库事务和约束可以避免超额选课。

## 7. pgvector 是什么

pgvector 是 PostgreSQL 的向量扩展，用来做相似度检索。

它主要服务于 AI 助教的课程知识库问答。

普通数据库擅长查精确字段，例如：

```text
查找 course_id = 1 的课程
查找 user_id = 2 的选课记录
```

向量检索擅长查语义相似内容，例如：

```text
学生问：“梯度下降为什么要沿着负梯度方向走？”

系统检索到：
- 机器学习课件第 3 章中的梯度下降定义
- 教师上传讲义里的优化算法说明
- 论坛中教师关于学习率的精选回答
```

### 7.1 pgvector 的结构

知识库相关表可以这样设计：

```text
knowledge_documents
- id
- course_id
- title
- source_type
- source_url
- parse_status
- created_at

knowledge_chunks
- id
- document_id
- course_id
- content
- embedding
- chunk_index
- created_at
```

其中 `embedding` 就是文本向量。

### 7.2 pgvector 的特点

- 直接和 PostgreSQL 放在一起，第一版部署简单。
- 不需要额外维护独立向量数据库。
- 适合早期课程知识库规模不太大的情况。
- 后期如果资料非常多，可以迁移到 Qdrant 或 Milvus。

### 7.3 pgvector 在 AI 问答里的流程

```text
教师上传课件
  |
  v
解析课件文本
  |
  v
切分成多个 chunk
  |
  v
生成 embedding
  |
  v
存入 knowledge_chunks
```

学生提问时：

```text
学生问题
  |
  v
生成问题 embedding
  |
  v
在 pgvector 中检索相似 chunk
  |
  v
把检索结果放进 Prompt
  |
  v
调用大模型生成回答
```

## 8. Redis 是什么

Redis 是内存型数据存储，速度很快，常用于缓存、限流、验证码、任务队列。

在本项目中，Redis 可以负责：

- 登录验证码缓存。
- 用户登录状态辅助缓存。
- 热门课程缓存。
- 热门帖子缓存。
- AI 问答限流。
- 防止用户频繁提交。
- 后台任务队列中间件。

### 8.1 Redis 的结构

Redis 不是按表存储，而是按 key-value 存储。

示例：

```text
captcha:login:13800000000 -> 928431
rate_limit:assistant:user_001 -> 10
course:hot:list -> [...]
task:parse_document:doc_001 -> pending
```

### 8.2 Redis 的特点

- 读写速度快。
- 适合保存临时数据。
- 支持过期时间。
- 支持计数器，适合限流。
- 可以作为 Celery / RQ 的任务队列后端。

### 8.3 Redis 在项目里的例子

AI 助教限流：

```text
用户每提问一次
  |
  v
Redis 中 user_id 对应计数 +1
  |
  v
如果一分钟超过限制，则拒绝请求
```

这样可以避免某个用户大量调用 AI，导致费用或系统压力失控。

## 9. MinIO 是什么

MinIO 是对象存储服务，可以理解为自建版的 S3 文件存储。

在本项目中，MinIO 保存：

- 用户头像。
- 课程封面。
- 教师上传的课件。
- PDF、PPT、Word 文件。
- 论坛图片。
- 学习报告导出文件。

数据库里不建议直接保存大文件本体，只保存文件地址或 object key。

例如：

```text
course_materials
- id
- course_id
- file_name
- object_key
- file_type
- file_size
- uploaded_by
- created_at
```

真正文件保存在 MinIO：

```text
guochuang-materials/course_001/chapter_02/gradient-descent.pdf
```

### 9.1 MinIO 的特点

- 适合保存大量文件。
- 可以本地部署。
- 接口兼容 S3 生态。
- 比把文件放进数据库更合理。
- 后期可以迁移到云厂商对象存储。

### 9.2 MinIO 在项目里的例子

教师上传课件：

```text
React 上传文件
  |
  v
FastAPI 接收文件
  |
  v
上传到 MinIO
  |
  v
PostgreSQL 保存文件元数据
  |
  v
创建课件解析任务
```

## 10. Docker Compose 是什么

Docker Compose 是本地和服务器上编排多个容器的工具。

你们的项目不只有一个程序，而是有：

- 前端。
- 后端。
- 数据库。
- Redis。
- MinIO。
- 向量检索能力。

如果每个都手动安装，会非常麻烦。Docker Compose 可以用一个配置文件把它们一起启动。

### 10.1 Docker Compose 结构

```text
deploy/docker-compose.yml
```

里面可以定义：

```text
web
api
postgres
redis
minio
```

启动：

```text
docker compose up -d
```

停止：

```text
docker compose down
```

### 10.2 Docker Compose 的特点

- 统一开发环境。
- 避免“我电脑能跑，你电脑不能跑”。
- 数据库、Redis、MinIO 一键启动。
- 适合第一版部署和演示。
- 后期可以迁移到 Kubernetes 或云服务。

## 11. AI 大模型 API 是什么

AI 大模型 API 是系统调用外部或本地大模型的接口。

在本项目中，大模型负责：

- 回答学生问题。
- 根据课程资料解释知识点。
- 总结学习报告。
- 给教师生成答疑建议。
- 根据论坛讨论生成问题摘要。

AI 助教不应该只是简单把问题丢给大模型。更合理的是 RAG：

```text
课程资料 + 检索结果 + 用户问题 -> 大模型回答
```

这样回答会更贴合课程内容，也更容易给出引用来源。

### 11.1 AI 助教模块结构

```text
apps/api/app/modules/assistant/
├── api.py
├── schemas.py
├── chat_service.py
├── retrieval_service.py
├── prompt_builder.py
├── knowledge_ingestion.py
├── models.py
└── repository.py
```

基础设施层：

```text
apps/api/app/infrastructure/
├── llm_client.py
├── vector_store.py
└── object_storage.py
```

### 11.2 AI 助教的特点

- 可以成为项目亮点。
- 能结合课程资料，不只是通用聊天。
- 可以保存问答记录，用于学习分析。
- 可以根据学生提问发现薄弱知识点。
- 需要做限流、日志、成本控制和内容安全。

## 12. Nginx 是什么

Nginx 是 Web 服务器和反向代理。

在本项目中，Nginx 可以负责：

- 部署前端静态文件。
- 把 `/api` 请求转发给 FastAPI。
- 配置 HTTPS。
- 统一入口域名。

部署后访问结构：

```text
https://your-domain.com
  |
  +--> React 前端页面
  |
  +--> /api/* 转发到 FastAPI
```

### 12.1 Nginx 的特点

- 稳定成熟。
- 适合部署前端静态资源。
- 可以隐藏后端真实端口。
- 可以配置 HTTPS。
- 可以做基础限流和压缩。

## 13. 每个部分之间的关系

### 13.1 登录流程

```text
React 登录表单
  |
  v
FastAPI /api/auth/login
  |
  v
PostgreSQL 查询用户
  |
  v
校验密码
  |
  v
返回 JWT token
  |
  v
React 保存 token 并进入系统
```

### 13.2 课程选择流程

```text
React 点击选课
  |
  v
FastAPI /api/courses/{id}/enroll
  |
  v
PostgreSQL 检查课程容量、用户身份、重复选课
  |
  v
写入 enrollments
  |
  v
返回成功
```

### 13.3 论坛发帖流程

```text
React 发帖编辑器
  |
  v
FastAPI /api/courses/{id}/posts
  |
  v
PostgreSQL 保存帖子
  |
  v
返回帖子详情
```

如果帖子里有图片：

```text
图片 -> FastAPI -> MinIO
帖子内容 -> PostgreSQL
```

### 13.4 AI 问答流程

```text
React AI 聊天框
  |
  v
FastAPI assistant 模块
  |
  v
Redis 检查限流
  |
  v
PostgreSQL 保存用户问题
  |
  v
pgvector 检索课程资料
  |
  v
大模型 API 生成回答
  |
  v
PostgreSQL 保存 AI 回答
  |
  v
React 展示答案
```

### 13.5 课件上传与知识库流程

```text
教师在 React 上传课件
  |
  v
FastAPI 接收文件
  |
  v
MinIO 保存文件
  |
  v
PostgreSQL 保存课件元数据
  |
  v
Redis / Celery 创建解析任务
  |
  v
后台任务解析文本、切片、向量化
  |
  v
pgvector 保存向量
```

### 13.6 学习报告流程

```text
学生浏览课程、提问、发帖
  |
  v
FastAPI 写入 learning_events
  |
  v
PostgreSQL 保存学习行为
  |
  v
定时任务统计数据
  |
  v
生成 learning_reports
  |
  v
React 展示报告
```

## 14. 第一版为什么这样搭配

这套技术栈的核心思路是：

```text
React 负责界面
FastAPI 负责业务接口
PostgreSQL 负责可靠数据
pgvector 负责课程知识库检索
Redis 负责临时数据和任务
MinIO 负责文件
Docker Compose 负责一键运行
```

它的特点：

- 学习成本相对可控。
- 适合学生团队分工。
- 适合快速做出可演示系统。
- 对 AI 助教功能非常友好。
- 后续可以平滑扩展，不需要推翻重做。
- 前后端、数据库、AI、文件、部署边界清楚。

## 15. 第一版开发顺序建议

建议不要一开始就同时做所有模块。可以按下面顺序：

```text
1. 搭建 Monorepo 目录
2. 搭建 React 前端空项目
3. 搭建 FastAPI 后端空项目
4. 接入 PostgreSQL
5. 实现用户注册登录
6. 实现课程列表、课程详情、选课
7. 实现论坛发帖和回帖
8. 接入 MinIO，支持课件上传
9. 接入 pgvector，建立课程知识库
10. 实现 AI 助教问答
11. 记录学习行为
12. 生成学习报告
13. 用 Docker Compose 统一启动
```

第一版可以先把 AI 助教做成“基础问答”，再逐步升级为“基于课程资料的 RAG 问答”。这样更容易控制开发进度。

## 16. 简短总结

如果把系统比作一个学校里的智能学习平台：

```text
React 是学生和老师看到的教室界面。
FastAPI 是处理所有请求的教务系统。
PostgreSQL 是保存正式档案的数据库。
pgvector 是能按语义查资料的知识库索引。
Redis 是临时记事本和高速缓存。
MinIO 是课件资料室。
Docker Compose 是一键启动整栋教学楼的工具。
大模型 API 是 AI 助教的大脑。
```

第一版最重要的是把边界划清楚：界面归前端，业务归后端，结构化数据归 PostgreSQL，文件归 MinIO，临时数据归 Redis，语义检索归 pgvector，智能回答归 AI 助教模块。这样项目越做越大时，代码也不会乱。
