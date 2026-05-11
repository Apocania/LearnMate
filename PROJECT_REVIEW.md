# LearnMate 项目重新审查报告

审查时间：2026-05-11  
项目位置：`/home/apocania/LearnMate`  
项目定位：面向师生教学场景的智能伴学系统平台  
当前阶段：可演示的早期原型，已经具备核心业务雏形，但还不是生产级系统。

## 1. 总体结论

LearnMate 当前已经不只是空框架，而是一个前后端打通的教学平台原型。

已经具备：

- React + TypeScript + Vite 前端。
- FastAPI + SQLAlchemy 后端。
- PostgreSQL、Redis、MinIO 的 Docker Compose 基础配置。
- 登录注册。
- 学生、伴学师两种身份。
- Token 鉴权。
- 游客浏览、学生操作、伴学师管理的基础权限体系。
- 课程创建、编辑、删除、浏览。
- 学生加入课程、退出课程。
- 讨论区发帖、评论、点赞、伴学师删除帖子。
- 课件上传、浏览、下载、删除。
- 文件大小和类型限制。
- AI伴学聊天页面和后端接口调用。
- 个人中心/学习报告展示页。
- 前端顶部导航和儿童教育风格 UI。
- 路由懒加载拆包。
- 基础后端测试。

仍然不完整：

- AI 仍是占位回答，没有接真实大模型。
- RAG 检索仍是占位，没有 embedding、pgvector、资料切片和引用来源。
- 学习记录和学习报告仍是静态展示，没有真实数据闭环。
- 数据库迁移还不规范，仍主要依赖 `create_all()` 和开发期 SQL 补丁。
- 课程没有章节体系，课件没有绑定到具体课程。
- 论坛没有分页、课程筛选、评论删除、内容审核。
- 文件仍是本地磁盘存储，没有真正使用 MinIO。
- 部署配置仍有不一致风险，尤其是 `.env.example` 中旧项目名和旧数据库名。
- 测试覆盖很少，只能证明基础路径正常。

一句话判断：

> 当前项目适合继续开发、课程设计展示和基础功能演示；如果要上线给真实用户使用，还需要补数据库迁移、部署配置、AI能力、学习数据闭环和更完整的测试。

## 2. 本次验证结果

### 2.1 前端构建

命令：

```bash
npm run build --prefix apps/web
```

结果：通过。

说明：

- TypeScript 构建通过。
- Vite 打包通过。
- 已经启用路由懒加载。
- 当前主业务入口包约 `131KB`，比之前所有页面打进一个约 `1MB` 主包的状态好很多。

### 2.2 后端语法检查

命令：

```bash
python3 -m compileall apps/api/app
```

结果：通过。

说明：后端 Python 文件没有语法错误。

### 2.3 后端测试

命令：

```bash
APP_ENV=test apps/api/.venv/bin/python -m pytest apps/api/tests
```

结果：

```text
2 passed
```

当前测试包括：

- 健康检查接口。
- 注册时非法用户名校验。

测试输出里有 FastAPI `on_event` 弃用警告，这不是当前功能错误，但后续建议改成 lifespan。

### 2.4 Docker Compose 配置检查

命令：

```bash
docker compose -f deploy/docker-compose.yml config
```

结果：语法通过。

但发现一个重要风险：

- `deploy/env.example` 已经是 LearnMate 和容器服务名配置。
- `apps/api/.env.example` 仍保留 `Guochuang API`、`guochuang` 数据库名、`guochuang-materials` bucket。
- `deploy/docker-compose.yml` 读取 `../apps/api/.env`。
- 如果 `.env` 是从旧的 `apps/api/.env.example` 复制来的，API 容器会使用 `localhost` 连接数据库，容器内会连不到 postgres 服务。

这是当前部署层最容易踩坑的问题之一。

## 3. 当前项目结构

核心目录：

```text
LearnMate/
├── apps/
│   ├── web/                  # React 前端
│   └── api/                  # FastAPI 后端
├── deploy/                   # Docker Compose、Nginx、部署说明
├── docs/                     # 设计文档
├── data/                     # 示例数据、知识库资料占位
├── packages/                 # 共享类型占位
├── PROJECT_REVIEW.md         # 本审查报告
├── README.md
├── package.json
└── package-lock.json
```

这是一个 Monorepo 结构，前端、后端、部署和文档放在一个仓库里。对当前阶段是合适的，因为前后端接口变化频繁，放在一起方便同步开发。

## 4. 前端审查

### 4.1 技术栈

前端位于：

```text
apps/web/
```

主要技术：

- React
- TypeScript
- Vite
- React Router
- Ant Design

### 4.2 路由

路由文件：

```text
apps/web/src/app/router.tsx
```

当前路由：

```text
/login        登录注册页
/             首页
/courses      课程中心
/courses/:id  课程详情占位
/forum        讨论交流
/files        文件资料
/assistant    AI伴学
/reports/me   个人中心
```

优点：

- 页面分工清晰。
- 已使用 `React.lazy` 和 `Suspense` 做路由懒加载。
- 构建后各页面拆成独立 chunk，首屏 JS 压力降低。

不足：

- 还没有真正的 `ProtectedRoute` 组件。
- 当前策略是允许游客打开页面，再在页面内部隐藏或禁用操作。
- 对于 `AI伴学`、`个人中心` 这种更偏登录后功能的页面，后续可以考虑路由级登录守卫。

### 4.3 顶部导航和 UI

布局文件：

```text
apps/web/src/components/AppLayout.tsx
```

当前顶部导航从左到右是：

```text
LearnMate 标志
课程中心
讨论交流
AI伴学
个人中心
登录/用户身份
```

优点：

- 已从侧边栏改成顶部导航。
- 风格更接近儿童教育网站：亮色、圆角、轻快。
- 登录后显示用户名和身份。
- 支持退出登录。

不足：

- 登录状态从 `localStorage` 直接读取，不是响应式全局状态。
- 如果多标签页登录/退出，当前页面不会自动同步刷新。
- 还没有用户头像、个人资料编辑等能力。

### 4.4 API 请求封装

文件：

```text
apps/web/src/api/client.ts
```

当前能力：

- 自动拼接 `VITE_API_BASE_URL`。
- 自动附加 Bearer token。
- FormData 上传时不会错误添加 JSON header。
- 可以处理 `204 No Content`。
- 遇到 `401` 会清除本地 token 并跳转登录页。

优点：

- 请求逻辑集中。
- 解决了删除接口返回空内容时前端解析失败的问题。
- 失效登录态不会长期留在本地。

风险：

- token 存在 `localStorage`，有 XSS 风险。
- 没有请求超时、重试和取消机制。
- 后续如果请求变多，建议引入 TanStack Query 管理缓存、刷新、错误状态。

### 4.5 登录注册页

文件：

```text
apps/web/src/pages/LoginPage.tsx
```

当前能力：

- 登录。
- 注册。
- 注册时选择学生或伴学师。
- 注册时确认密码。
- 用户名规则说明。
- 登录成功后保存 token 和用户信息。

优点：

- 表单体验比旧版完整。
- 前端和后端都有用户名规则校验。

不足：

- 没有验证码。
- 没有找回密码。
- 没有登录失败次数限制。
- 没有 refresh token。

### 4.6 课程中心

文件：

```text
apps/web/src/pages/CourseListPage.tsx
```

当前能力：

- 游客可以浏览课程。
- 学生可以加入课程、退出课程。
- 伴学师可以创建、编辑、删除自己创建的课程。
- 课程显示学习人数和当前学生是否已加入。
- 支持关键词搜索。
- 课程状态使用下拉选择：已发布、草稿。
- 伴学师可以从课程中心进入课件管理。

优点：

- 已从单纯 CRUD 升级为有角色区分的课程模块。
- 前后端都有权限限制，不只是前端隐藏按钮。

不足：

- 没有分页。
- 没有课程封面。
- 没有课程容量、开课时间、分类、难度。
- 没有章节。
- 课件没有绑定到课程。
- 学生加入课程后，还没有“我的课程”视图。

### 4.7 讨论交流

文件：

```text
apps/web/src/pages/ForumPage.tsx
```

当前能力：

- 游客可以浏览帖子和评论。
- 登录用户可以发帖、评论、点赞。
- 伴学师可以删除帖子。
- 帖子显示点赞数、评论数、是否已点赞。

优点：

- 基础互动闭环完整。
- 游客浏览体验已经比旧版好。
- 伴学师具备初步论坛管理能力。

不足：

- 帖子不能编辑。
- 评论不能删除。
- 没有分页。
- 没有按课程筛选。
- 没有内容审核、敏感词、举报。
- 伴学师删除帖子是硬删除。

### 4.8 文件资料

文件：

```text
apps/web/src/pages/FilesPage.tsx
```

当前能力：

- 游客和学生可以浏览、下载课件。
- 伴学师可以上传课件。
- 伴学师可以删除自己上传的课件。
- 上传使用 FormData。
- 前端展示上传者、文件大小、类型。

后端限制：

- 默认最大 `20MB`。
- 默认允许 PDF、PNG、JPG、TXT、DOCX。

优点：

- 比旧版多了类型限制、大小限制、删除能力和角色限制。
- 文件名使用 UUID 存储，避免重名覆盖。

不足：

- 仍是本地磁盘存储，不是 MinIO。
- 大文件仍会一次性读入内存。
- 没有病毒扫描。
- 下载接口未鉴权，任何拿到链接的人都能访问。
- 文件没有绑定课程。
- 删除文件会删除磁盘文件和数据库记录，没有回收站。

### 4.9 AI伴学

文件：

```text
apps/web/src/pages/AssistantPage.tsx
```

当前能力：

- 登录后可以输入问题。
- 前端会真实调用后端 `/api/assistant/messages`。
- 后端返回后，前端会显示回答。
- 游客不能使用 AI，会看到登录提示。

优点：

- 已经从纯静态聊天框升级为前后端打通。
- 页面交互路径完整。

不足：

- 后端 `LLMClient` 仍返回占位回答。
- `VectorStore.search()` 仍返回空数组。
- 没有真实大模型调用。
- 没有课程资料检索。
- 没有引用来源。
- 没有保存对话记录。
- 没有流式输出。

### 4.10 个人中心/学习报告

文件：

```text
apps/web/src/pages/LearningReportPage.tsx
```

当前状态：

- 页面 UI 存在。
- 显示学习时长、完成章节、AI 问答次数、能力进度、学习轨迹。

不足：

- 数据是静态假数据。
- 没有调用后端报告接口。
- 没有真实学习记录。
- 没有区分学生视角和伴学师视角。

## 5. 后端审查

### 5.1 后端入口

文件：

```text
apps/api/app/main.py
```

当前能力：

- 创建 FastAPI 应用。
- 配置 CORS。
- 注册健康检查接口。
- 注册 auth、users、courses、forum、files、assistant、learning_records、reports 路由。
- 非测试环境启动时初始化数据库。

优点：

- 模块注册清晰。
- `APP_ENV=test` 时跳过数据库初始化，方便跑轻量测试。

不足：

- 使用 `@app.on_event("startup")`，当前 FastAPI 已提示该写法弃用，后续建议改 lifespan。
- 初始化数据库仍依赖 `create_all()` 和手写 SQL 补丁。

### 5.2 配置

文件：

```text
apps/api/app/core/config.py
```

当前配置包括：

- 数据库。
- Redis。
- JWT。
- CORS。
- MinIO。
- LLM。
- 上传文件大小。
- 上传文件类型白名单。

优点：

- 配置集中。
- 文件上传限制已经配置化。

风险：

- `JWT_SECRET` 默认是 `change-me-in-production`，生产必须修改。
- `apps/api/.env.example` 仍保留旧项目名和旧数据库配置。
- 本地运行和 Docker 运行的 `DATABASE_URL` 主机名不同，容易混淆。

### 5.3 鉴权与身份

位置：

```text
apps/api/app/modules/auth/
```

当前能力：

- 注册。
- 登录。
- 密码 PBKDF2 哈希。
- HMAC token。
- 当前用户解析。
- 可选当前用户解析。
- 角色权限工具。

当前角色：

```text
student
mentor
```

优点：

- 密码不是明文。
- 已经有 token 过期。
- 已经支持游客访问部分接口。
- 后端真正检查角色，不只靠前端按钮。
- 用户名会标准化为小写，并限制为英文、数字、下划线。

不足：

- token 不是标准 JWT。
- 没有 refresh token。
- 没有登出黑名单。
- 没有登录失败次数限制。
- 没有邮箱/手机号验证。

### 5.4 课程模块

位置：

```text
apps/api/app/modules/courses/
```

当前接口：

```text
GET    /api/courses
POST   /api/courses
GET    /api/courses/{course_id}
PUT    /api/courses/{course_id}
DELETE /api/courses/{course_id}
POST   /api/courses/{course_id}/enroll
DELETE /api/courses/{course_id}/enroll
```

数据表：

```text
courses
course_enrollments
```

当前权限：

- 游客可浏览课程。
- 学生可加入/退出课程。
- 伴学师可创建课程。
- 伴学师只能编辑/删除自己创建的课程。

优点：

- 课程核心权限已经比较清楚。
- 选课关系已经落库。
- 返回课程时会带学习人数和本人是否加入。

不足：

- 选课没有容量限制。
- 没有课程章节。
- 没有课程资料关联。
- 没有课程状态枚举约束，后端仍接收字符串。
- 删除课程是硬删除。

### 5.5 论坛模块

位置：

```text
apps/api/app/modules/forum/
```

当前接口：

```text
GET    /api/forum/posts
POST   /api/forum/posts
GET    /api/forum/posts/{post_id}/comments
POST   /api/forum/posts/{post_id}/comments
POST   /api/forum/posts/{post_id}/like
DELETE /api/forum/posts/{post_id}
```

当前权限：

- 游客可浏览帖子和评论。
- 学生和伴学师可发帖、评论、点赞。
- 伴学师可删除帖子。

优点：

- 点赞有唯一约束，避免重复点赞。
- 返回帖子的统计字段较完整。
- 管理能力已经有雏形。

不足：

- 没有分页。
- 没有课程维度筛选。
- 删除帖子会级联清理评论和点赞，但不是软删除。
- 没有编辑帖子。
- 没有删除评论。
- 没有审核机制。

### 5.6 文件模块

位置：

```text
apps/api/app/modules/files/
```

当前接口：

```text
GET    /api/files
POST   /api/files/upload
GET    /api/files/{file_id}/download
DELETE /api/files/{file_id}
```

当前权限：

- 所有人可浏览文件列表。
- 所有人可下载文件。
- 只有伴学师可上传文件。
- 伴学师只能删除自己上传的文件。

优点：

- 已有文件大小限制。
- 已有类型白名单。
- 已有删除文件功能。
- 元数据存入数据库。

不足：

- 本地磁盘存储不适合多服务器部署。
- 未使用 MinIO。
- 文件没有课程归属。
- 下载未鉴权。
- 大文件一次性读入内存。

### 5.7 AI 模块

位置：

```text
apps/api/app/modules/assistant/
```

当前接口：

```text
POST /api/assistant/messages
```

当前流程：

```text
用户问题
  -> AssistantChatService
  -> RetrievalService
  -> VectorStore.search，占位
  -> prompt_builder
  -> LLMClient.chat，占位
```

优点：

- 模块边界已经预留得比较清楚。
- 前端已经接入该接口。
- 接口要求登录。

不足：

- 没有真实 LLM。
- 没有 embedding。
- 没有向量检索。
- 没有知识库入库。
- 没有引用来源。
- 没有会话记录。

### 5.8 学习记录与报告

位置：

```text
apps/api/app/modules/learning_records/
apps/api/app/modules/reports/
```

当前状态：

- 有模块目录、模型、接口、service、repository。
- 业务逻辑仍偏占位。

不足：

- 学生加入课程、浏览课程、使用 AI、发帖评论等行为还没有统一写入学习记录。
- 报告页没有接真实接口。
- 伴学师没有学生学习概览。

## 6. 数据库审查

当前数据库初始化：

```text
Base.metadata.create_all()
开发期 ALTER TABLE / CREATE INDEX 补丁
```

优点：

- 开发阶段启动方便。
- 旧表字段缺失时能部分自修复。

主要风险：

- 没有正式迁移版本。
- 表结构变更不容易多人同步。
- 字段删除、重命名、类型变更无法安全管理。
- 生产环境升级风险高。

项目依赖里已经有 `alembic`，并且 `apps/api/migrations` 目录存在，但当前还没有形成完整迁移工作流。下一步应该把已有 schema 固化成第一版 Alembic migration。

## 7. 部署审查

部署目录：

```text
deploy/
```

当前内容：

- `docker-compose.yml`
- `env.example`
- Nginx 配置
- 部署说明

优点：

- PostgreSQL 使用 `pgvector/pgvector:pg16`，为后续 RAG 检索留了基础。
- Redis、MinIO 服务已经在 Compose 中。
- 前端和后端都有 Dockerfile。

主要问题：

- `apps/api/.env.example` 仍是旧的 `Guochuang` 配置。
- Compose 读取 `apps/api/.env`，而不是 `deploy/env.example`。
- 如果 `.env` 中 `DATABASE_URL` 是 `localhost`，API 容器内会连不上 postgres。
- MinIO 配置存在，但代码还没有真正使用 MinIO。
- 生产环境的 `JWT_SECRET`、数据库密码、MinIO 密钥都需要替换。

建议：

- 统一 `.env.example`。
- 明确区分本地开发 `.env.local` 和 Docker `.env.docker`。
- Compose 中直接提供安全的默认开发环境变量，或改为读取 `deploy/.env`。

## 8. 当前优点

### 8.1 架构边界清楚

前端、后端、部署、文档分离。后端按模块拆分，模块内部有 api、schemas、models、repository、service，适合继续扩展。

### 8.2 核心业务已形成闭环

登录、课程、选课、讨论、文件、AI 请求都已经有前端入口和后端接口。

### 8.3 权限体系开始成型

游客、学生、伴学师的能力差异已经在前后端同时体现。

### 8.4 UI 已经可演示

顶部导航和儿童教育风格比早期后台风格更符合 LearnMate 定位。

### 8.5 构建体积明显改善

路由懒加载后，构建结果拆成多个 chunk，主入口包大幅降低。

### 8.6 测试开始建立

已经能运行 pytest，并有基础测试。虽然覆盖还少，但测试链路已经打通。

## 9. 当前主要缺点与风险

### 9.1 AI 能力仍是最大短板

平台名字包含“智能伴学”，但当前 AI 仍是占位回答。演示时可以说明“接口已打通”，但不能宣称已经具备真实智能答疑能力。

### 9.2 学习数据没有闭环

学生选课、发帖、评论、AI 提问等行为还没有沉淀为学习记录，因此个人中心的数据仍是假的。

### 9.3 数据库迁移不规范

多人协作和部署升级时，必须尽快从 `create_all()` 转向 Alembic。

### 9.4 部署配置容易混乱

当前 `.env.example` 和 `deploy/env.example` 不一致，是新同学部署时最容易出错的地方。

### 9.5 文件系统不适合生产

本地上传目录适合开发，但不适合多实例部署、备份、权限控制和对象存储管理。

### 9.6 测试覆盖不足

目前只有 2 个测试，无法覆盖课程权限、论坛权限、文件限制和 AI 鉴权等核心行为。

## 10. 完整性评分

按“早期原型”标准重新估计：

| 模块 | 完整度 | 说明 |
|---|---:|---|
| 项目结构 | 85% | Monorepo 清晰，模块边界明确 |
| 登录注册 | 75% | 可用，有基础校验，缺生产级安全 |
| 角色权限 | 70% | 游客/学生/伴学师规则已落地，仍缺更细权限模型 |
| 课程模块 | 70% | CRUD 和选课可用，缺章节、资料绑定 |
| 论坛模块 | 65% | 互动闭环可用，缺分页、筛选、审核 |
| 文件模块 | 60% | 上传下载删除可用，有限制，缺 MinIO 和课程绑定 |
| AI伴学 | 30% | 前后端打通，但智能能力仍占位 |
| 学习报告 | 20% | UI 有，数据未接真实业务 |
| 前端 UI | 80% | 顶部导航和教育风格已成型 |
| 测试 | 20% | 测试链路可用，但覆盖很少 |
| 部署 | 50% | Compose 语法可用，但配置一致性有风险 |

总体：

```text
早期原型完成度：约 65% - 70%
```

相比上一版，主要提升来自：

- 角色权限落地。
- 学生选课落地。
- 文件上传安全增强。
- AI 页面开始真实调用后端。
- 路由懒加载优化包体积。
- 测试依赖和基础测试补齐。

## 11. 下一步优先级

### 第一优先级：修稳定性和部署坑

1. 统一 `apps/api/.env.example` 和 `deploy/env.example`。
2. 明确本地运行和 Docker 运行的数据库地址。
3. 把 FastAPI startup 从 `on_event` 迁移到 lifespan。
4. 建立 Alembic 第一版迁移。
5. 补课程权限、论坛权限、文件上传限制的接口测试。

### 第二优先级：补教学核心业务

1. 增加课程章节。
2. 让课件绑定到课程。
3. 增加“我的课程”页面。
4. 论坛支持按课程筛选。
5. 学生学习行为写入 learning_records。

### 第三优先级：做真正 AI伴学

1. 上传课件后解析文本。
2. 文本切分 chunk。
3. 生成 embedding。
4. 存入 pgvector。
5. 用户提问时检索课程资料。
6. 调用真实大模型。
7. 返回回答和引用来源。
8. 保存对话记录。

### 第四优先级：完善生产化能力

1. 文件迁移到 MinIO。
2. 下载鉴权。
3. 登录失败次数限制。
4. refresh token。
5. 内容审核和举报。
6. 管理后台。
7. 监控和日志。

## 12. 推荐演示路径

当前可以这样演示：

1. 注册伴学师账号。
2. 进入课程中心创建课程。
3. 编辑课程状态。
4. 进入课件管理上传课件。
5. 注册学生账号。
6. 浏览课程并加入课程。
7. 进入讨论交流发帖、评论、点赞。
8. 切回伴学师账号删除不合适帖子。
9. 打开 AI伴学提问，说明当前接口已打通，后续接入真实 RAG。
10. 打开个人中心，说明这里将承载真实学习报告。

## 13. 推荐阅读代码顺序

如果要完整理解当前项目，建议按这个顺序读：

```text
1. apps/web/src/app/router.tsx
2. apps/web/src/components/AppLayout.tsx
3. apps/web/src/api/client.ts
4. apps/web/src/pages/CourseListPage.tsx
5. apps/web/src/pages/ForumPage.tsx
6. apps/web/src/pages/FilesPage.tsx
7. apps/web/src/pages/AssistantPage.tsx
8. apps/api/app/main.py
9. apps/api/app/core/config.py
10. apps/api/app/core/database.py
11. apps/api/app/modules/auth/
12. apps/api/app/modules/courses/
13. apps/api/app/modules/forum/
14. apps/api/app/modules/files/
15. apps/api/app/modules/assistant/
```

这个顺序能从“用户如何进入页面”一路看到“请求如何到后端、权限如何判断、数据如何落库、结果如何返回前端”。

## 14. 当前不应提交的内容

这些内容不应进入 Git：

```text
apps/api/.env
apps/web/.env
apps/api/.venv/
node_modules/
apps/web/dist/
apps/api/storage/uploads/真实上传文件
__pycache__/
*.tsbuildinfo
```

当前 `PROJECT_REVIEW.md` 是项目审查文档，如果希望团队共享，可以提交；如果只是个人理解笔记，可以继续保持不提交。

## 15. 总结

LearnMate 当前已经是一个“能演示、能继续扩展”的教学平台原型。

它的强项是：

- 项目结构清楚。
- 前后端已打通。
- 权限规则已经开始落地。
- 课程、论坛、文件等基础教学功能可用。
- UI 风格已经贴近儿童教育网站。

它的主要短板是：

- AI 还不是真智能。
- 学习报告没有真实数据。
- 数据库迁移和部署配置还不够规范。
- 文件存储仍是开发期方案。
- 测试覆盖不足。

下一阶段最值得做的是：先统一环境配置和 Alembic 迁移，再把课件绑定课程、学习行为写入记录，最后把 AI伴学从占位回答升级为基于课程资料的 RAG 问答。
