# Guochuang 项目结构说明

本文档详细说明 `guochuang` 智能伴学系统当前基础框架的目录结构、每个文件的意义、作用、当前内容，以及后续应该如何扩展。

这个项目采用 Monorepo 组织方式，也就是把前端、后端、部署、文档、数据样例和共享包放在同一个仓库中管理。

## 1. 总体结构

当前项目结构可以概括为：

```text
guochuang/
├── apps/                  # 可运行的应用
│   ├── web/               # React 前端应用
│   └── api/               # FastAPI 后端应用
├── packages/              # 多应用共享的代码或类型
├── docs/                  # 项目设计文档
├── deploy/                # 部署相关配置
├── data/                  # 示例数据和知识库资料
├── README.md              # 项目入口说明
├── PROJECT_STRUCTURE.md   # 当前项目结构说明
├── ARCHITECTURE.md        # 架构设计说明
├── TECH_STACK_V1.md       # 第一版技术栈说明
├── COMMAND_LINE_GUIDE.md  # 命令行教程
├── SERVER_MIGRATION_GUIDE.md # 服务器迁移指南
├── package.json           # Monorepo 根配置
└── .gitignore             # Git 忽略规则
```

最重要的划分规则：

```text
apps      放真正能运行的程序
docs      放文档
deploy    放部署配置
data      放示例数据和资料
packages  放共享代码
```

## 2. 根目录文件

### 2.1 `README.md`

位置：

```text
guochuang/README.md
```

作用：

项目入口说明。别人第一次打开项目时，应该先看这个文件。

当前内容：

- 项目简介。
- 第一版技术栈。
- 顶层目录说明。
- 前端、后端、基础服务的启动命令。

后续可以继续补充：

- 项目背景。
- 团队成员。
- 开发规范。
- 演示账号。
- 常用链接。

### 2.2 `PROJECT_STRUCTURE.md`

位置：

```text
guochuang/PROJECT_STRUCTURE.md
```

作用：

详细解释项目目录和文件用途。它不是业务代码，而是给开发者看的“地图”。

适合在这些场景使用：

- 新成员加入项目。
- 不知道文件应该放哪里。
- 想理解前后端怎么组织。
- 想判断目录是否需要继续细分。

### 2.3 `ARCHITECTURE.md`

位置：

```text
guochuang/ARCHITECTURE.md
```

作用：

说明系统整体架构。

当前内容包括：

- 为什么推荐前后端分离。
- 为什么第一版采用模块化单体。
- AI 助教如何采用 RAG 架构。
- 数据库、Redis、MinIO、向量库如何协作。
- 后续如何演进为局部微服务。

### 2.4 `TECH_STACK_V1.md`

位置：

```text
guochuang/TECH_STACK_V1.md
```

作用：

详细解释第一版技术栈中每个组件是什么。

当前内容包括：

- React 是什么。
- TypeScript 是什么。
- Vite 是什么。
- FastAPI 是什么。
- PostgreSQL 和 pgvector 是什么。
- Redis 是什么。
- MinIO 是什么。
- Docker Compose 是什么。

### 2.5 `COMMAND_LINE_GUIDE.md`

位置：

```text
guochuang/COMMAND_LINE_GUIDE.md
```

作用：

命令行教程和命令速查表。

适合对命令行不熟的同学使用。

当前内容包括：

- `cd`、`ls`、`mkdir` 等基础命令。
- Git 命令。
- npm / React 命令。
- Python / FastAPI 命令。
- Docker Compose 命令。
- PostgreSQL、Redis、MinIO 命令。
- 常见报错处理。

### 2.6 `SERVER_MIGRATION_GUIDE.md`

位置：

```text
guochuang/SERVER_MIGRATION_GUIDE.md
```

作用：

说明如何把项目迁移部署到另一台服务器。

当前内容包括：

- 迁移代码。
- 迁移 PostgreSQL。
- 迁移 MinIO 文件。
- 修改 `.env`。
- 修改 Nginx。
- 配置域名、HTTPS、防火墙。
- 迁移后检查清单。

### 2.7 `package.json`

位置：

```text
guochuang/package.json
```

作用：

Monorepo 根配置。

当前内容：

```json
{
  "name": "guochuang",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "dev:web": "npm --prefix apps/web run dev",
    "build:web": "npm --prefix apps/web run build",
    "preview:web": "npm --prefix apps/web run preview"
  },
  "workspaces": [
    "apps/web",
    "packages/*"
  ]
}
```

它的意义：

- `private: true`：防止误发布到 npm。
- `scripts`：可以从根目录运行前端命令。
- `workspaces`：声明前端和共享包属于同一个工作区。

示例：

```bash
npm run dev:web
```

等价于：

```bash
cd apps/web
npm run dev
```

### 2.8 `.gitignore`

位置：

```text
guochuang/.gitignore
```

作用：

告诉 Git 哪些文件不要提交。

当前忽略：

- `node_modules/`：前端依赖。
- `.venv/`：Python 虚拟环境。
- `__pycache__/`：Python 编译缓存。
- `dist/`：前端构建产物。
- `.env`：本地环境变量和密钥。
- 日志文件。
- 编辑器配置。

为什么重要：

这些文件要么很大，要么每个人本地都不同，要么包含敏感信息，不应该进入代码仓库。

## 3. `apps`：可运行应用目录

位置：

```text
guochuang/apps/
```

作用：

存放真正可以启动运行的应用。

当前包含：

```text
apps/
├── web/  # React 前端
└── api/  # FastAPI 后端
```

为什么叫 `apps`：

`apps` 是 applications 的缩写，表示这里面放的是“应用程序”。前端和后端都是应用，而不是普通工具函数或文档。

以后可以扩展：

```text
apps/
├── web/
├── api/
├── ai-service/
├── worker/
└── mobile/
```

## 4. 前端应用：`apps/web`

位置：

```text
guochuang/apps/web/
```

作用：

React + TypeScript + Vite 前端应用。它负责用户界面，包括登录、课程、论坛、AI 助教、学习报告等页面。

当前结构：

```text
apps/web/
├── src/
├── package.json
├── index.html
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
├── nginx.conf
├── .env.example
└── README.md
```

### 4.1 `apps/web/package.json`

作用：

前端应用的 npm 配置文件。

当前内容包括：

- 项目名：`@guochuang/web`
- 脚本：
  - `dev`：启动 Vite 开发服务器。
  - `build`：执行 TypeScript 检查并构建生产文件。
  - `preview`：预览构建结果。
- 依赖：
  - `react`
  - `react-dom`
  - `react-router-dom`
- 开发依赖：
  - `vite`
  - `typescript`
  - `@vitejs/plugin-react`
  - React 类型声明。

常用命令：

```bash
cd apps/web
npm install
npm run dev
npm run build
```

### 4.2 `apps/web/index.html`

作用：

前端页面的 HTML 入口。

当前内容：

- 设置页面语言为中文。
- 设置移动端 viewport。
- 定义 `<div id="root"></div>`。
- 加载 `/src/main.tsx`。

React 会把整个应用渲染到：

```html
<div id="root"></div>
```

### 4.3 `apps/web/tsconfig.json`

作用：

TypeScript 配置文件。

当前内容：

- 启用严格类型检查。
- 支持 React JSX。
- 使用现代 ES 模块。
- 只检查 `src` 目录。

它保证前端代码在类型层面更可靠。

### 4.4 `apps/web/vite.config.ts`

作用：

Vite 构建工具配置。

当前内容：

- 启用 React 插件。
- 开发服务器端口设置为 `5173`。

### 4.5 `apps/web/.env.example`

作用：

前端环境变量模板。

当前内容：

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

意义：

前端通过这个地址请求后端 API。

实际开发时复制：

```bash
cp .env.example .env
```

注意：

Vite 规定暴露给前端的环境变量必须以 `VITE_` 开头。

### 4.6 `apps/web/Dockerfile`

作用：

定义如何把前端应用构建成 Docker 镜像。

当前流程：

```text
第一阶段：使用 node 镜像安装依赖并执行 npm run build
第二阶段：使用 nginx 镜像托管 dist 静态文件
```

它适合部署时把 React 前端打包为静态站点。

### 4.7 `apps/web/nginx.conf`

作用：

前端容器内部的 Nginx 配置。

当前内容：

- 监听 80 端口。
- 静态文件目录为 `/usr/share/nginx/html`。
- `try_files` 支持 React Router 的前端路由。

为什么需要 `try_files`：

如果用户直接访问：

```text
/courses/123
```

Nginx 实际上找不到这个物理文件，需要回退到 `index.html`，再由 React Router 接管路由。

### 4.8 `apps/web/README.md`

作用：

前端应用自己的说明文档。

当前内容：

- 如何安装依赖。
- 如何复制 `.env`。
- 如何启动前端。

## 5. 前端源码：`apps/web/src`

位置：

```text
apps/web/src/
```

作用：

存放 React 前端所有源码。

当前结构：

```text
src/
├── main.tsx
├── styles.css
├── app/
├── pages/
├── components/
├── api/
├── shared/
└── features/
```

### 5.1 `src/main.tsx`

作用：

React 应用入口文件。

当前内容：

- 引入 React。
- 引入 ReactDOM。
- 引入 React Router。
- 引入全局样式。
- 把应用挂载到 `#root`。

它是前端真正开始运行的地方。

### 5.2 `src/styles.css`

作用：

全局样式文件。

当前内容：

- 设置全局字体、背景、文字颜色。
- 设置盒模型。
- 定义主布局类：
  - `.app-shell`
  - `.sidebar`
  - `.main`
  - `.panel`
  - `.grid`
- 定义移动端响应式布局。

后续建议：

如果引入 Ant Design、Tailwind 或 CSS Modules，可以逐渐减少全局样式，把页面样式放到组件附近。

## 6. 前端 `src/app`

位置：

```text
apps/web/src/app/
```

作用：

存放整个 React 应用的全局配置。

当前文件：

```text
router.tsx
providers.tsx
```

### 6.1 `src/app/router.tsx`

作用：

定义前端路由。

当前路由：

```text
/login           登录页
/                学习首页
/courses         课程中心
/courses/:id     课程详情
/forum           论坛交流
/assistant       AI 助教
/reports/me      我的学习报告
```

它把 URL 和页面组件对应起来。

后续新增页面时，通常要修改这个文件。

### 6.2 `src/app/providers.tsx`

作用：

预留全局 Provider 位置。

当前内容：

只是返回 `children`。

后续可以加入：

- React Query 的 `QueryClientProvider`。
- 主题 Provider。
- 用户认证 Provider。
- 国际化 Provider。

## 7. 前端 `src/pages`

位置：

```text
apps/web/src/pages/
```

作用：

存放页面级组件。页面通常对应一个路由。

当前文件：

```text
LoginPage.tsx
DashboardPage.tsx
CourseListPage.tsx
CourseDetailPage.tsx
ForumPage.tsx
AssistantPage.tsx
LearningReportPage.tsx
```

### 7.1 `LoginPage.tsx`

作用：

登录页面。

当前内容：

显示系统名和登录功能占位说明。

后续应加入：

- 用户名/密码输入框。
- 登录按钮。
- 调用 `api/auth.ts`。
- 登录成功保存 token。
- 跳转首页。

### 7.2 `DashboardPage.tsx`

作用：

学习首页。

当前内容：

展示三个入口面板：

- 我的课程。
- AI 助教。
- 学习报告。

后续应接入：

- 最近学习课程。
- 学习进度。
- 待办事项。
- 最近问答。

### 7.3 `CourseListPage.tsx`

作用：

课程列表页面。

当前内容：

显示课程中心标题和课程列表待接入提示。

后续应调用：

```text
GET /api/courses
```

并展示课程卡片、筛选、搜索和选课状态。

### 7.4 `CourseDetailPage.tsx`

作用：

课程详情页面。

当前内容：

显示课程详情占位。

后续应展示：

- 课程介绍。
- 教师信息。
- 章节列表。
- 课件资料。
- 选课按钮。
- 课程论坛入口。
- AI 助教入口。

### 7.5 `ForumPage.tsx`

作用：

论坛交流页面。

当前内容：

显示论坛功能占位。

后续应支持：

- 帖子列表。
- 发帖。
- 回帖。
- 点赞。
- 置顶。
- 教师答疑。

### 7.6 `AssistantPage.tsx`

作用：

AI 助教页面。

当前内容：

显示 AI 聊天和 RAG 检索功能占位。

后续应支持：

- 聊天输入框。
- 消息列表。
- 流式回答。
- 课程选择。
- 引用来源展示。
- 用户反馈。

### 7.7 `LearningReportPage.tsx`

作用：

学习报告页面。

当前内容：

显示报告功能占位。

后续应展示：

- 学习时长。
- 课程进度。
- 提问次数。
- 论坛互动。
- AI 总结建议。
- 薄弱知识点。

## 8. 前端 `src/components`

位置：

```text
apps/web/src/components/
```

作用：

存放通用 UI 组件。这些组件不强绑定某一个业务模块。

当前文件：

```text
AppLayout.tsx
PageHeader.tsx
EmptyState.tsx
```

### 8.1 `AppLayout.tsx`

作用：

应用主布局。

当前内容：

- 左侧侧边栏。
- 系统名称。
- 导航链接。
- 右侧主内容区域。
- 使用 `Outlet` 展示当前路由页面。

后续可扩展：

- 用户头像。
- 角色菜单。
- 退出登录。
- 权限控制。
- 移动端导航。

### 8.2 `PageHeader.tsx`

作用：

页面标题组件。

当前 props：

```ts
type PageHeaderProps = {
  title: string;
  description?: string;
};
```

适合在每个页面顶部显示标题和说明。

### 8.3 `EmptyState.tsx`

作用：

空状态组件。

当前 props：

```ts
type EmptyStateProps = {
  title: string;
  description?: string;
};
```

适合在列表为空、功能未接入、暂无数据时显示。

## 9. 前端 `src/api`

位置：

```text
apps/web/src/api/
```

作用：

封装前端对后端 API 的请求。

当前文件：

```text
client.ts
auth.ts
courses.ts
forum.ts
assistant.ts
reports.ts
```

### 9.1 `client.ts`

作用：

统一封装请求方法。

当前内容：

- 从 `VITE_API_BASE_URL` 读取 API 基础地址。
- 默认地址是 `http://localhost:8000/api`。
- 封装 `request<T>()` 方法。
- 请求失败时抛出错误。

后续可扩展：

- 自动携带 token。
- 统一处理 401 登录失效。
- 统一错误提示。
- 请求超时。

### 9.2 `auth.ts`

作用：

登录认证相关接口。

当前内容：

- `LoginRequest`
- `LoginResponse`
- `login()`

对应后端：

```text
POST /api/auth/login
```

### 9.3 `courses.ts`

作用：

课程相关接口。

当前内容：

- `CourseSummary`
- `listCourses()`

对应后端：

```text
GET /api/courses
```

### 9.4 `forum.ts`

作用：

论坛相关接口。

当前内容：

- `listPosts()`

对应后端：

```text
GET /api/forum/posts
```

### 9.5 `assistant.ts`

作用：

AI 助教相关接口。

当前内容：

- `AssistantMessageRequest`
- `sendAssistantMessage()`

对应后端：

```text
POST /api/assistant/messages
```

### 9.6 `reports.ts`

作用：

学习报告相关接口。

当前内容：

- `getMyLearningReports()`

对应后端：

```text
GET /api/reports/me
```

## 10. 前端 `src/shared`

位置：

```text
apps/web/src/shared/
```

作用：

存放前端内部共享的类型、工具函数和常量。

当前结构：

```text
shared/
├── types/
│   └── user.ts
└── utils/
    └── formatDate.ts
```

### 10.1 `shared/types/user.ts`

作用：

定义用户相关共享类型。

当前内容：

```ts
export type UserRole = "student" | "teacher" | "admin";

export type CurrentUser = {
  id: string;
  username: string;
  role: UserRole;
};
```

这些类型可以被登录、权限、用户菜单等多个地方使用。

### 10.2 `shared/utils/formatDate.ts`

作用：

日期格式化工具。

当前内容：

把字符串或 Date 格式化成中文日期。

适合课程时间、帖子时间、报告生成时间等场景使用。

## 11. 前端 `src/features`

位置：

```text
apps/web/src/features/
```

作用：

存放业务功能模块。

当前目录：

```text
features/
├── auth/
├── courses/
├── forum/
├── assistant/
└── reports/
```

当前这些目录暂时为空，是预留扩展位置。

后续建议：

```text
features/courses/
├── CourseCard.tsx
├── EnrollButton.tsx
├── useCourseList.ts
└── courseTypes.ts
```

为什么需要 `features`：

页面负责组织布局，feature 负责具体业务功能。这样页面不会越来越臃肿。

## 12. 后端应用：`apps/api`

位置：

```text
guochuang/apps/api/
```

作用：

FastAPI 后端应用，负责业务接口、数据库访问、权限、AI 助教、学习记录等功能。

当前结构：

```text
apps/api/
├── app/
├── tests/
├── migrations/
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md
```

### 12.1 `apps/api/requirements.txt`

作用：

Python 依赖列表。

当前依赖：

- `fastapi`：后端 API 框架。
- `uvicorn`：ASGI 服务器，用来启动 FastAPI。
- `pydantic-settings`：读取环境变量配置。
- `sqlalchemy`：数据库 ORM。
- `alembic`：数据库迁移。
- `psycopg`：PostgreSQL 驱动。
- `redis`：Redis 客户端。
- `python-multipart`：支持文件上传。

安装命令：

```bash
pip install -r requirements.txt
```

### 12.2 `apps/api/pyproject.toml`

作用：

Python 项目配置文件。

当前内容：

- 项目名。
- Python 版本要求。
- Ruff 代码风格配置。
- Pytest 测试配置。

后续如果使用 Poetry、uv 或更完整的打包方式，也可以在这里扩展。

### 12.3 `apps/api/.env.example`

作用：

后端环境变量模板。

当前内容包括：

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `CORS_ORIGINS`
- `MINIO_ENDPOINT`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`

实际开发时复制：

```bash
cp .env.example .env
```

注意：

`.env` 不应该提交到 Git，因为里面可能包含数据库密码和 AI API Key。

### 12.4 `apps/api/Dockerfile`

作用：

定义如何构建后端 Docker 镜像。

当前流程：

```text
使用 python:3.12-slim
设置工作目录 /app
安装 requirements.txt
复制项目代码
启动 uvicorn app.main:app
```

### 12.5 `apps/api/README.md`

作用：

后端应用自己的说明文档。

当前内容：

- 创建虚拟环境。
- 安装依赖。
- 复制 `.env`。
- 启动 FastAPI。
- 访问健康检查和接口文档。

### 12.6 `apps/api/migrations`

作用：

数据库迁移目录。

当前为空。

后续使用 Alembic 后，这里会生成数据库版本文件。

常见命令：

```bash
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

### 12.7 `apps/api/tests`

作用：

后端测试目录。

当前文件：

```text
test_health.py
```

后续建议按模块增加测试：

```text
tests/test_auth.py
tests/test_courses.py
tests/test_assistant.py
```

## 13. 后端源码：`apps/api/app`

位置：

```text
apps/api/app/
```

作用：

FastAPI 后端源码主目录。

当前结构：

```text
app/
├── main.py
├── core/
├── modules/
├── infrastructure/
├── common/
└── __init__.py
```

### 13.1 `app/main.py`

作用：

FastAPI 应用入口。

当前内容：

- 创建 FastAPI app。
- 配置 CORS。
- 定义健康检查接口：

```text
GET /api/health
```

- 注册业务模块路由：

```text
/api/auth
/api/users
/api/courses
/api/forum
/api/assistant
/api/learning-records
/api/reports
```

它不应该写复杂业务逻辑，只负责组装应用。

### 13.2 `app/__init__.py`

作用：

声明 `app` 是 Python 包。

当前内容：

只有包说明字符串。

## 14. 后端 `app/core`

位置：

```text
apps/api/app/core/
```

作用：

存放整个后端都依赖的核心配置。

当前文件：

```text
config.py
database.py
security.py
__init__.py
```

### 14.1 `core/config.py`

作用：

读取和管理环境变量。

当前内容：

- 定义 `Settings`。
- 读取数据库、Redis、JWT、CORS、MinIO、大模型配置。
- 使用 `.env` 文件。
- 提供全局 `settings`。

示例：

```python
settings.database_url
settings.redis_url
settings.cors_origins
```

后续所有配置都应该优先加到这里，而不是散落在业务代码中。

### 14.2 `core/database.py`

作用：

数据库连接配置。

当前内容：

- 定义 SQLAlchemy `Base`。
- 创建数据库引擎 `engine`。
- 创建会话工厂 `SessionLocal`。
- 提供依赖函数 `get_db()`。

后续数据库模型都应该继承：

```python
Base
```

### 14.3 `core/security.py`

作用：

安全相关工具。

当前内容：

- `get_password_hash()`
- `verify_password()`
- `create_access_token()`

注意：

当前只是开发占位实现，不适合生产环境。

后续需要替换为：

- bcrypt / passlib 密码哈希。
- 正式 JWT 签名。
- token 解析和权限依赖。

## 15. 后端 `app/common`

位置：

```text
apps/api/app/common/
```

作用：

存放真正跨模块通用的后端工具。

当前文件：

```text
responses.py
exceptions.py
pagination.py
__init__.py
```

### 15.1 `common/responses.py`

作用：

统一成功响应格式。

当前内容：

```python
def success(data: Any = None, message: str = "ok") -> dict[str, Any]:
  return {"success": True, "data": data, "message": message}
```

后续可以加入统一错误响应、request_id 等。

### 15.2 `common/exceptions.py`

作用：

定义业务异常。

当前内容：

```python
class BusinessError(Exception)
```

后续可以配合 FastAPI exception handler，把业务异常转换成统一错误响应。

### 15.3 `common/pagination.py`

作用：

分页参数模型。

当前内容：

```python
class PageParams(BaseModel):
  page: int = 1
  page_size: int = 20
```

适合课程列表、帖子列表、报告列表等接口使用。

## 16. 后端 `app/infrastructure`

位置：

```text
apps/api/app/infrastructure/
```

作用：

存放外部基础设施客户端。这里不是业务逻辑，而是连接外部系统的代码。

当前文件：

```text
redis.py
object_storage.py
vector_store.py
llm_client.py
__init__.py
```

### 16.1 `infrastructure/redis.py`

作用：

创建 Redis 客户端。

当前内容：

```python
def get_redis_client() -> Redis:
  return Redis.from_url(settings.redis_url, decode_responses=True)
```

后续用于：

- 验证码。
- 限流。
- 缓存。
- 任务队列。

### 16.2 `infrastructure/object_storage.py`

作用：

对象存储客户端，占位用于接入 MinIO。

当前内容：

```python
class ObjectStorageClient:
  def put_object(...)
```

后续应该实现：

- 上传文件到 MinIO。
- 下载文件。
- 生成访问 URL。
- 删除文件。

### 16.3 `infrastructure/vector_store.py`

作用：

向量检索客户端，占位用于接入 pgvector。

当前内容：

```python
class VectorStore:
  def search(...)
```

后续用于 AI 助教：

- 保存 embedding。
- 检索相似课程资料。
- 返回引用片段。

### 16.4 `infrastructure/llm_client.py`

作用：

大模型调用客户端。

当前内容：

```python
class LLMClient:
  def chat(self, prompt: str) -> str
```

当前返回占位回答。

后续应该接入真实模型服务，例如 OpenAI-compatible API、本地模型服务等。

## 17. 后端 `app/modules`

位置：

```text
apps/api/app/modules/
```

作用：

存放业务模块。每个模块代表一个业务边界。

当前模块：

```text
auth
users
courses
forum
assistant
learning_records
reports
```

为什么这样拆：

- 登录认证归 `auth`。
- 用户资料归 `users`。
- 课程和选课归 `courses`。
- 论坛发帖回帖归 `forum`。
- AI 问答归 `assistant`。
- 学习行为归 `learning_records`。
- 学习报告归 `reports`。

## 18. 后端模块内部文件规则

大部分模块遵循下面结构：

```text
api.py          路由和 HTTP 接口
schemas.py      请求和响应数据模型
service.py      业务逻辑
models.py       数据库模型
repository.py   数据库访问
__init__.py     Python 包声明
```

### 18.1 `api.py`

负责：

- 定义接口路径。
- 接收请求参数。
- 调用 service。
- 返回响应。

不应该写复杂业务规则。

### 18.2 `schemas.py`

负责：

- 定义请求体。
- 定义响应体。
- 做字段校验。

FastAPI 会根据它自动生成接口文档。

### 18.3 `service.py`

负责：

- 核心业务流程。
- 权限判断。
- 状态判断。
- 调用多个 repository 或 infrastructure。

例如课程选课时，应该在 service 判断：

- 课程是否存在。
- 课程是否已发布。
- 是否已经选过。
- 是否超过容量。

### 18.4 `models.py`

负责：

定义数据库表对应的 SQLAlchemy 模型。

例如：

```python
class Course(Base):
  __tablename__ = "courses"
```

### 18.5 `repository.py`

负责：

- 查询数据库。
- 插入数据。
- 更新数据。
- 删除或软删除数据。

业务规则不应该写在 repository 中。

## 19. `auth` 模块

位置：

```text
apps/api/app/modules/auth/
```

作用：

认证和登录模块。

当前文件：

```text
api.py
schemas.py
service.py
models.py
repository.py
__init__.py
```

当前功能：

- `POST /api/auth/login`
- 接收用户名和密码。
- 返回开发占位 token。

当前 `models.py` 定义了：

```text
User
```

包含：

- `id`
- `username`
- `password_hash`
- `role`

后续需要实现：

- 注册。
- 密码加密。
- JWT 正式签名。
- token 解析。
- 用户权限依赖。

## 20. `users` 模块

位置：

```text
apps/api/app/modules/users/
```

作用：

用户资料和当前用户信息模块。

当前文件：

```text
api.py
__init__.py
```

当前功能：

```text
GET /api/users/me
```

返回开发占位用户：

```json
{
  "id": "dev-user",
  "username": "student1",
  "role": "student"
}
```

后续可以补充：

- `schemas.py`
- `service.py`
- `repository.py`
- 用户资料修改。
- 用户列表。
- 用户状态管理。

## 21. `courses` 模块

位置：

```text
apps/api/app/modules/courses/
```

作用：

课程和选课模块。

当前功能：

```text
GET  /api/courses
GET  /api/courses/{course_id}
POST /api/courses/{course_id}/enroll
```

当前文件：

- `api.py`：定义课程接口。
- `schemas.py`：定义 `CourseSummary`。
- `models.py`：定义 `Course`。
- `service.py`：业务服务占位。
- `repository.py`：数据库访问占位。

后续需要实现：

- 课程创建。
- 课程编辑。
- 章节管理。
- 课件管理。
- 选课容量检查。
- 退课。
- 教师课程管理。

## 22. `forum` 模块

位置：

```text
apps/api/app/modules/forum/
```

作用：

论坛交流模块。

当前功能：

```text
GET /api/forum/posts
```

当前文件：

- `api.py`：帖子列表接口占位。
- `schemas.py`：定义 `ForumPostSummary`。
- `models.py`：定义 `ForumPost`。
- `service.py`：业务服务占位。
- `repository.py`：数据库访问占位。

后续需要实现：

- 发帖。
- 帖子详情。
- 回帖。
- 点赞。
- 置顶。
- 删除。
- 课程内论坛。

## 23. `assistant` 模块

位置：

```text
apps/api/app/modules/assistant/
```

作用：

AI 助教模块，是项目智能化能力的核心。

当前文件：

```text
api.py
schemas.py
chat_service.py
retrieval_service.py
prompt_builder.py
knowledge_ingestion.py
models.py
repository.py
__init__.py
```

为什么比其他模块拆得更细：

AI 助教内部职责更多，包括聊天、检索、Prompt 构造、课件入库、向量化、对话记录，所以需要更细的文件边界。

### 23.1 `assistant/api.py`

当前功能：

```text
POST /api/assistant/messages
```

接收学生问题，调用 `AssistantChatService`，返回回答和引用。

### 23.2 `assistant/schemas.py`

定义：

- `AssistantMessageRequest`
- `AssistantCitation`
- `AssistantMessageResponse`

这些结构会出现在接口文档中。

### 23.3 `assistant/chat_service.py`

作用：

AI 聊天业务编排。

当前流程：

```text
用户问题
  |
  v
RetrievalService 检索资料
  |
  v
prompt_builder 构造 Prompt
  |
  v
LLMClient 调用模型
```

### 23.4 `assistant/retrieval_service.py`

作用：

课程资料检索服务。

当前调用：

```python
VectorStore.search()
```

后续会接入 pgvector，检索和问题语义相似的课程资料片段。

### 23.5 `assistant/prompt_builder.py`

作用：

构造大模型 Prompt。

当前内容：

把课程资料片段和学生问题组合成提示词。

后续可以扩展：

- 控制回答风格。
- 要求引用来源。
- 限制只回答课程相关内容。
- 加入安全规则。

### 23.6 `assistant/knowledge_ingestion.py`

作用：

知识库入库服务。

当前是占位。

后续流程：

```text
教师上传课件
解析文本
切分 chunk
生成 embedding
保存到 pgvector
```

### 23.7 `assistant/models.py`

当前定义：

```text
AssistantSession
```

后续还需要：

- `AssistantMessage`
- `KnowledgeDocument`
- `KnowledgeChunk`

### 23.8 `assistant/repository.py`

作用：

AI 对话、知识库记录的数据库访问，占位待实现。

## 24. `learning_records` 模块

位置：

```text
apps/api/app/modules/learning_records/
```

作用：

学习行为记录模块。

当前功能：

```text
GET /api/learning-records
```

当前文件：

- `api.py`
- `schemas.py`
- `models.py`
- `service.py`
- `repository.py`

当前 `schemas.py` 定义：

```text
LearningEventRequest
```

当前 `models.py` 定义：

```text
LearningEvent
```

后续要记录：

- 浏览课程。
- 查看课件。
- 提问 AI。
- 发帖回帖。
- 完成任务。
- 观看视频。

## 25. `reports` 模块

位置：

```text
apps/api/app/modules/reports/
```

作用：

学习报告模块。

当前功能：

```text
GET /api/reports/me
```

当前文件：

- `api.py`
- `schemas.py`
- `models.py`
- `service.py`
- `repository.py`

当前 `schemas.py` 定义：

```text
LearningReportSummary
```

当前 `models.py` 定义：

```text
LearningReport
```

后续要实现：

- 个人周报。
- 课程报告。
- 教师班级报告。
- AI 总结建议。
- 学习趋势图。

## 26. 后端测试文件

### 26.1 `apps/api/tests/test_health.py`

作用：

测试健康检查接口。

当前内容：

- 创建 `TestClient`。
- 请求 `/api/health`。
- 断言状态码是 200。
- 断言返回 `status` 是 `ok`。

意义：

这是最小后端测试，用于确认 FastAPI 应用能正常启动并响应。

后续建议：

- 为登录写测试。
- 为课程选课写测试。
- 为 AI 问答写 mock 测试。
- 为学习报告统计写测试。

## 27. `deploy` 部署目录

位置：

```text
guochuang/deploy/
```

作用：

存放部署相关配置，不属于前端或后端单独所有。

当前文件：

```text
docker-compose.yml
env.example
README.md
nginx/guochuang.conf
```

### 27.1 `deploy/docker-compose.yml`

作用：

用 Docker Compose 一键启动多个服务。

当前服务：

```text
postgres  PostgreSQL + pgvector
redis     Redis
minio     MinIO 对象存储
api       FastAPI 后端
web       React 前端静态服务
```

当前端口：

```text
5432  PostgreSQL
6379  Redis
9000  MinIO API
9001  MinIO 控制台
8000  FastAPI
5173  前端 Web
```

注意：

`api` 服务读取：

```text
../apps/api/.env
```

所以第一次启动前需要：

```bash
cp deploy/env.example apps/api/.env
```

### 27.2 `deploy/env.example`

作用：

Docker Compose 环境下的后端 `.env` 模板。

和 `apps/api/.env.example` 的区别：

- `apps/api/.env.example` 默认适合本机开发，数据库地址是 `localhost`。
- `deploy/env.example` 适合容器网络，数据库地址是 `postgres`，Redis 地址是 `redis`，MinIO 地址是 `minio`。

### 27.3 `deploy/README.md`

作用：

部署目录说明。

当前内容：

- 复制 `.env`。
- 启动基础服务。
- 启动全部服务。
- 常用访问地址。

### 27.4 `deploy/nginx/guochuang.conf`

作用：

服务器 Nginx 配置示例。

当前内容：

- 前端静态文件目录：

```text
/opt/guochuang/apps/web/dist
```

- `/api/` 反向代理到：

```text
http://127.0.0.1:8000/api/
```

部署到真实服务器时需要修改：

- `server_name`
- `root`
- `proxy_pass`
- HTTPS 证书配置。

## 28. `docs` 文档目录

位置：

```text
guochuang/docs/
```

作用：

存放项目详细设计文档。

当前文件：

```text
README.md
api-design.md
database-design.md
ai-assistant-design.md
deployment.md
```

### 28.1 `docs/README.md`

作用：

说明文档目录应该放什么。

当前建议后续补充：

- `PRD.md`
- `PDD.md`
- `api-design.md`
- `database-design.md`
- `ai-assistant-design.md`
- `deployment.md`

### 28.2 `docs/api-design.md`

作用：

接口设计文档占位。

当前记录建议接口前缀：

```text
/api/auth
/api/users
/api/courses
/api/forum
/api/assistant
/api/reports
```

后续应该写清楚：

- 请求方法。
- 请求路径。
- 请求参数。
- 响应格式。
- 错误码。

### 28.3 `docs/database-design.md`

作用：

数据库设计文档占位。

当前记录核心表建议：

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
knowledge_documents
knowledge_chunks
learning_events
learning_reports
```

后续应该补充字段、索引、关系图和迁移说明。

### 28.4 `docs/ai-assistant-design.md`

作用：

AI 助教设计文档占位。

当前记录 RAG 基本流程：

```text
用户问题 -> 向量检索课程资料 -> 构造 Prompt -> 调用大模型 -> 返回带引用的回答
```

后续应该补充：

- 文档解析方案。
- chunk 切分策略。
- embedding 模型。
- pgvector 表结构。
- Prompt 模板。
- 安全策略。

### 28.5 `docs/deployment.md`

作用：

部署设计文档占位。

当前记录建议服务：

```text
postgres
redis
minio
api
web/nginx
```

后续应该补充服务器部署步骤。

## 29. `data` 数据目录

位置：

```text
guochuang/data/
```

作用：

存放开发和演示用的数据，不是正式数据库。

当前结构：

```text
data/
├── seed/
└── knowledge-base/
```

### 29.1 `data/seed/README.md`

作用：

说明这里存放初始化测试数据。

后续可以加入：

- 测试用户。
- 示例课程。
- 示例论坛帖子。
- 演示学习记录。

### 29.2 `data/knowledge-base/README.md`

作用：

说明这里可以放 AI 助教演示用课程资料样例。

注意：

生产环境真实课件应该上传到 MinIO，数据库只保存文件元数据。

## 30. `packages` 共享包目录

位置：

```text
guochuang/packages/
```

作用：

存放多个应用共享的代码或类型。

当前结构：

```text
packages/
└── shared-types/
```

### 30.1 `packages/shared-types/README.md`

作用：

说明共享类型目录用途。

当前只是占位。

后续适合放：

- 用户角色枚举。
- 课程状态枚举。
- 统一 API 响应类型。
- 前后端共享的协议定义。

第一版不建议过度使用 `packages`。只有当前端和后端确实需要共享稳定定义时，再往这里添加内容。

## 31. 当前项目请求链路

以课程列表为例：

```text
浏览器访问 /courses
  |
  v
React Router 匹配 CourseListPage.tsx
  |
  v
后续页面调用 apps/web/src/api/courses.ts
  |
  v
GET http://localhost:8000/api/courses
  |
  v
FastAPI app/main.py 注册 courses_router
  |
  v
apps/api/app/modules/courses/api.py
  |
  v
返回课程数据
```

以 AI 问答为例：

```text
AssistantPage.tsx
  |
  v
apps/web/src/api/assistant.ts
  |
  v
POST /api/assistant/messages
  |
  v
assistant/api.py
  |
  v
AssistantChatService
  |
  +--> RetrievalService
  |      |
  |      v
  |    VectorStore
  |
  +--> prompt_builder
  |
  +--> LLMClient
```

## 32. 新增功能时文件应该放哪里

### 32.1 新增一个前端页面

例如新增“教师课程管理”页面：

```text
apps/web/src/pages/TeacherCourseManagePage.tsx
```

然后在：

```text
apps/web/src/app/router.tsx
```

增加路由。

### 32.2 新增一个前端业务组件

例如课程卡片：

如果只给课程模块使用：

```text
apps/web/src/features/courses/CourseCard.tsx
```

如果很多模块都使用：

```text
apps/web/src/components/CourseCard.tsx
```

### 32.3 新增一个后端业务模块

例如通知模块：

```text
apps/api/app/modules/notifications/
├── __init__.py
├── api.py
├── schemas.py
├── service.py
├── models.py
└── repository.py
```

然后在：

```text
apps/api/app/main.py
```

注册路由。

### 32.4 新增一个外部服务客户端

例如邮件服务：

```text
apps/api/app/infrastructure/email_client.py
```

不要放进某个业务模块，除非它只服务那个模块。

### 32.5 新增接口文档

放到：

```text
docs/api-design.md
```

### 32.6 新增数据库表说明

放到：

```text
docs/database-design.md
```

实际迁移文件放到：

```text
apps/api/migrations/
```

## 33. 不应该怎么放

不要把所有前端组件都放到：

```text
src/components/
```

如果组件只属于课程模块，应放在：

```text
src/features/courses/
```

不要把所有后端代码按技术类型堆成：

```text
controllers/
services/
models/
```

当前项目更推荐按业务模块组织：

```text
modules/courses/
modules/forum/
modules/assistant/
```

不要把业务逻辑写在：

```text
app/main.py
```

`main.py` 只负责创建 app 和注册路由。

不要把真实密钥写入：

```text
.env.example
```

真实密钥只应该写在本地 `.env` 或服务器环境变量中。

不要提交：

```text
node_modules/
.venv/
__pycache__/
dist/
.env
```

这些已经被 `.gitignore` 忽略。

## 34. 为什么有些目录现在是空的

例如：

```text
apps/web/src/features/auth/
apps/web/src/features/courses/
apps/web/src/features/forum/
apps/web/src/features/assistant/
apps/web/src/features/reports/
apps/api/migrations/
```

它们是预留的功能边界。

为什么可以先创建：

- 让团队提前形成约定。
- 后续开发知道文件应该放哪里。
- 避免所有功能堆到页面或主文件里。

为什么不继续细分更多：

第一版还没有真实业务代码，过度细分会增加理解成本。等某个模块变复杂，再继续拆。

## 35. 维护原则

后续开发时建议遵守：

```text
1. 页面放 pages，业务组件放 features，通用组件放 components。
2. 后端按业务模块放 modules，不要到处散落。
3. 外部系统连接放 infrastructure。
4. 全局配置放 core。
5. 真正通用的工具才放 common 或 shared。
6. 文档放 docs，部署放 deploy，示例数据放 data。
7. 不提交密钥、不提交依赖目录、不提交构建产物。
```

最核心的判断标准：

```text
这个文件属于哪个应用？
这个文件属于哪个业务？
这个文件是业务逻辑，还是技术连接？
这个文件是当前模块专用，还是全项目通用？
```

想清楚这四个问题，文件基本就不会放错。
