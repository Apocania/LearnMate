# 仓库合作者新电脑部署指南

## 1. 适用于一位新合作者在全新电脑、全新 VS Code 环境中，从零开始拉取并运行 LearnMate 项目。


## 2. 新电脑需要安装的软件

合作者需要先安装以下软件。

### 必装软件

| 软件 | 用途 | 下载地址 |
| --- | --- | --- |
| Git | 拉取代码、提交代码、分支协作 | <https://git-scm.com/downloads> |
| VS Code | 代码编辑器 | <https://code.visualstudio.com/> |
| Node.js LTS | 运行 React + Vite 前端 | <https://nodejs.org/> |
| Python 3.11 或 3.12 | 运行 FastAPI 后端 | <https://www.python.org/downloads/> |
| Docker Desktop | 启动 PostgreSQL、Redis、MinIO 等基础服务 | <https://www.docker.com/products/docker-desktop/> |

### 推荐安装

| 软件 | 用途 | 下载地址 |
| --- | --- | --- |
| GitHub CLI | 创建 PR、查看 PR、登录 GitHub | <https://cli.github.com/> |

### 检查安装是否成功

打开终端执行：

```bash
git --version
node -v
npm -v
python --version
docker --version
```

Windows 如果 `python --version` 不可用，可以尝试：

```bash
py --version
```

## 3. 配置 Git 身份

第一次使用 Git 时，需要设置提交者信息。

```bash
git config --global user.name "你的名字"
git config --global user.email "你的 GitHub 邮箱"
```

查看配置是否成功：

```bash
git config --global --list
```

## 4. 登录 GitHub 或配置 SSH

私有仓库需要认证后才能拉取。推荐使用 SSH，也可以使用 HTTPS。

### 方式 A：使用 HTTPS

```bash
git clone https://github.com/你的用户名/你的仓库名.git
```

如果 GitHub 要求登录，需要使用 GitHub 账号授权，或使用 Personal Access Token。

### 方式 B：使用 SSH

生成 SSH key：

```bash
ssh-keygen -t ed25519 -C "你的 GitHub 邮箱"
```

一路回车即可。

查看公钥。

macOS / Linux：

```bash
cat ~/.ssh/id_ed25519.pub
```

Windows PowerShell：

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

复制输出内容，然后打开 GitHub：

```text
头像 -> Settings -> SSH and GPG keys -> New SSH key
```

添加完成后测试：

```bash
ssh -T git@github.com
```

如果看到类似 `successfully authenticated` 的提示，说明 SSH 配置成功。

之后可以使用 SSH clone：

```bash
git clone git@github.com:你的用户名/你的仓库名.git
```

## 5. 克隆仓库并用 VS Code 打开

```bash
git clone git@github.com:你的用户名/你的仓库名.git
cd LearnMate
code .
```

如果 `code .` 不可用，可以手动打开 VS Code：

```text
File -> Open Folder -> 选择 LearnMate 文件夹
```

推荐安装 VS Code 插件：

- Python
- Pylance
- ESLint
- Prettier
- Docker
- GitLens，可选

## 6. 安装前端依赖

项目根目录有 `package.json`，推荐在项目根目录执行：

```bash
npm install
```

也可以只安装前端依赖：

```bash
cd apps/web
npm install
```

推荐使用根目录的 `npm install`，因为当前项目配置了 npm workspaces。

## 7. 准备环境变量文件

项目提供了 `.env.example` 示例文件。合作者需要复制为真正的 `.env` 文件。

### 前端环境变量

macOS / Linux：

```bash
cp apps/web/.env.example apps/web/.env
```

Windows PowerShell：

```powershell
Copy-Item apps/web/.env.example apps/web/.env
```

前端 `.env` 内容应类似：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 后端环境变量

macOS / Linux：

```bash
cp apps/api/.env.example apps/api/.env
```

Windows PowerShell：

```powershell
Copy-Item apps/api/.env.example apps/api/.env
```

本地开发时，后端 `apps/api/.env` 关键配置应类似：

```env
APP_ENV=development
APP_NAME=LearnMate API
DATABASE_URL=postgresql+psycopg://learnmate:learnmate@localhost:5432/learnmate
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change-me-in-production
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=learnmate-materials
LLM_PROVIDER=openai-compatible
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

如果暂时不用 AI 功能，`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 可以先留空。

## 8. 启动基础服务

确保 Docker Desktop 已经打开，然后在项目根目录执行：

```bash
cd deploy
docker compose up -d
```

这会启动：

| 服务 | 地址 |
| --- | --- |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |
| MinIO API | `localhost:9000` |
| MinIO 控制台 | `localhost:9001` |

回到项目根目录：

```bash
cd ..
```

查看容器状态：

```bash
docker compose -f deploy/docker-compose.yml ps
```

MinIO 控制台：

```text
http://localhost:9001
```

默认账号密码：

```text
minioadmin
minioadmin
```

## 9. 启动后端 FastAPI

进入后端目录：

```bash
cd apps/api
```

创建 Python 虚拟环境。

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装后端依赖：

```bash
pip install -r requirements.txt
```

启动后端：

```bash
uvicorn app.main:app --reload
```

后端默认地址：

```text
http://localhost:8000
```

接口文档地址：

```text
http://localhost:8000/docs
```

当前项目数据库表会在后端启动时通过 SQLAlchemy `create_all()` 初始化，一般不需要手动执行数据库迁移。

## 10. 启动前端

新开一个终端，回到项目根目录：

```bash
cd LearnMate
npm run dev:web
```

或者进入前端目录启动：

```bash
cd apps/web
npm run dev
```

前端默认地址：

```text
http://localhost:5173
```

浏览器访问该地址即可打开项目。

## 11. 推荐日常协作流程

不要直接在 `main` 分支上开发，建议每个任务新建一个功能分支。

### 开始新功能

```bash
git switch main
git pull origin main
git switch -c feature/功能名称
```

### 提交修改

```bash
git status
git add .
git commit -m "feat: 描述本次修改"
```

### 推送分支

```bash
git push -u origin feature/功能名称
```

### 创建 Pull Request

在 GitHub 页面创建 PR，或使用 GitHub CLI：

```bash
gh pr create --base main --head feature/功能名称 --title "feat: 描述本次修改"
```

### PR 合并后同步本地

```bash
git switch main
git pull origin main
git branch -d feature/功能名称
git fetch --prune
```

## 12. 最短首次启动命令汇总

macOS / Linux：

```bash
git clone git@github.com:你的用户名/你的仓库名.git
cd LearnMate
npm install
cp apps/web/.env.example apps/web/.env
cp apps/api/.env.example apps/api/.env
cd deploy
docker compose up -d
cd ../apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

另开一个终端：

```bash
cd LearnMate
npm run dev:web
```

Windows PowerShell：

```powershell
git clone git@github.com:你的用户名/你的仓库名.git
cd LearnMate
npm install
Copy-Item apps/web/.env.example apps/web/.env
Copy-Item apps/api/.env.example apps/api/.env
cd deploy
docker compose up -d
cd ../apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

另开一个 PowerShell：

```powershell
cd LearnMate
npm run dev:web
```

访问：

```text
http://localhost:5173
```

## 13. 常见报错与处理措施

### 13.1 `Repository not found`

可能原因：

- 合作者没有接受私有仓库邀请。
- 当前 GitHub 账号不是被邀请的账号。
- clone 地址写错。
- 使用 SSH 时没有配置 SSH key。

处理方式：

```bash
git remote -v
```

确认地址是否正确。然后让合作者检查 GitHub 邀请是否已接受。

如果使用 SSH，测试：

```bash
ssh -T git@github.com
```

### 13.2 `Permission denied (publickey)`

可能原因：SSH key 没有添加到 GitHub，或者本机没有正确加载 SSH key。

处理方式：

```bash
ssh-keygen -t ed25519 -C "你的 GitHub 邮箱"
```

把公钥添加到 GitHub：

```bash
cat ~/.ssh/id_ed25519.pub
```

Windows PowerShell：

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

添加后再次测试：

```bash
ssh -T git@github.com
```

### 13.3 `fatal: Authentication failed`

可能原因：HTTPS 方式 clone 时 GitHub 不再支持账号密码认证。

处理方式：

- 改用 SSH clone。
- 或者使用 GitHub Personal Access Token 作为密码。
- 或使用 GitHub CLI 登录：

```bash
gh auth login
```

### 13.4 `code: command not found`

可能原因：VS Code 的命令行工具没有加入 PATH。

处理方式：

在 VS Code 中按 `Ctrl + Shift + P` 或 `Cmd + Shift + P`，搜索：

```text
Shell Command: Install 'code' command in PATH
```

也可以手动打开 VS Code，再选择项目文件夹：

```text
File -> Open Folder
```

### 13.5 `npm: command not found`

可能原因：没有安装 Node.js，或安装后终端没有刷新 PATH。

处理方式：

1. 安装 Node.js LTS。
2. 关闭终端重新打开。
3. 检查：

```bash
node -v
npm -v
```

### 13.6 `npm install` 很慢或失败

可能原因：

- 网络访问 npm registry 不稳定。
- 公司或校园网络限制。
- 代理配置问题。

处理方式：

```bash
npm config get registry
```

可临时切换 registry：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

如果之后想恢复官方源：

```bash
npm config set registry https://registry.npmjs.org/
```

### 13.7 `docker: command not found`

可能原因：没有安装 Docker Desktop，或 Docker 没有加入 PATH。

处理方式：

1. 安装 Docker Desktop。
2. 启动 Docker Desktop。
3. 关闭终端后重新打开。
4. 检查：

```bash
docker --version
docker compose version
```

### 13.8 `Cannot connect to the Docker daemon`

可能原因：Docker Desktop 没有启动。

处理方式：

1. 打开 Docker Desktop。
2. 等待 Docker 状态变成 Running。
3. 重新执行：

```bash
docker compose -f deploy/docker-compose.yml ps
```

### 13.9 `port is already allocated` 或端口被占用

可能原因：本机已有其他服务占用了端口。

常见端口：

| 端口 | 服务 |
| --- | --- |
| `5173` | 前端 Vite |
| `8000` | 后端 FastAPI |
| `5432` | PostgreSQL |
| `6379` | Redis |
| `9000` | MinIO API |
| `9001` | MinIO 控制台 |

处理方式：

查看容器：

```bash
docker ps
```

如果是后端 `8000` 被占用，可以换端口：

```bash
uvicorn app.main:app --reload --port 8001
```

同时修改 `apps/web/.env`：

```env
VITE_API_BASE_URL=http://localhost:8001/api
```

然后重启前端。

### 13.10 `ModuleNotFoundError: No module named 'app'`

可能原因：后端启动命令执行目录不对。

处理方式：

确保在 `apps/api` 目录下启动：

```bash
cd apps/api
uvicorn app.main:app --reload
```

### 13.11 `uvicorn: command not found`

可能原因：

- 没有激活 Python 虚拟环境。
- 没有安装后端依赖。

处理方式：

macOS / Linux：

```bash
cd apps/api
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Windows PowerShell：

```powershell
cd apps/api
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 13.12 PowerShell 无法激活虚拟环境

报错可能类似：

```text
running scripts is disabled on this system
```

处理方式：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 13.13 `psycopg`、`pydantic`、`fastapi` 等 Python 依赖安装失败

可能原因：

- Python 版本过旧。
- pip 版本过旧。
- 网络问题。

处理方式：

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

如果本机同时有多个 Python 版本，确认当前版本：

```bash
python --version
```

建议使用 Python 3.11 或 3.12。

### 13.14 后端提示数据库连接失败

常见报错可能包含：

```text
connection refused
could not connect to server
Name or service not known
```

可能原因：

- PostgreSQL 容器没有启动。
- `.env` 里的 `DATABASE_URL` 不适合当前运行方式。
- Docker Desktop 没有启动。

处理方式：

确认基础服务：

```bash
docker compose -f deploy/docker-compose.yml ps
```

本地手动启动后端时，`apps/api/.env` 应使用：

```env
DATABASE_URL=postgresql+psycopg://learnmate:learnmate@localhost:5432/learnmate
```

如果是在 Docker Compose 容器中启动后端，才使用：

```env
DATABASE_URL=postgresql+psycopg://learnmate:learnmate@postgres:5432/learnmate
```

### 13.15 前端页面打开了，但接口请求失败

可能原因：

- 后端没有启动。
- 前端 `.env` 中 API 地址错误。
- 后端端口不是 `8000`。
- 修改 `.env` 后没有重启前端。

处理方式：

确认后端可访问：

```text
http://localhost:8000/docs
```

确认 `apps/web/.env`：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

修改 `.env` 后，停止前端并重新执行：

```bash
npm run dev:web
```

### 13.16 浏览器控制台出现 CORS 错误

可能原因：后端 `CORS_ORIGINS` 没有包含当前前端地址。

处理方式：

检查 `apps/api/.env`：

```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

如果 Vite 自动换成了其他端口，例如 `5174`，需要追加：

```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

然后重启后端。

### 13.17 `git push` 被拒绝

常见报错：

```text
rejected
fetch first
non-fast-forward
```

可能原因：远程分支比本地更新。

处理方式：

```bash
git pull --rebase
git push
```

如果有冲突，先解决冲突，再执行：

```bash
git add .
git rebase --continue
git push
```

### 13.18 合并或 rebase 出现冲突

处理方式：

查看冲突文件：

```bash
git status
```

打开文件，找到类似内容：

```text
<<<<<<< HEAD
当前分支内容
=======
对方分支内容
>>>>>>> branch-name
```

手动保留最终需要的内容，并删除冲突标记。然后：

```bash
git add .
```

如果是 merge：

```bash
git commit
```

如果是 rebase：

```bash
git rebase --continue
```

如果想放弃本次 rebase：

```bash
git rebase --abort
```

### 13.19 不小心在 main 分支上开发了

处理方式：

如果还没有提交：

```bash
git switch -c feature/功能名称
```

然后正常提交：

```bash
git add .
git commit -m "feat: 描述本次修改"
git push -u origin feature/功能名称
```

如果已经在 `main` 上提交了，但还没有 push：

```bash
git branch feature/功能名称
git reset --hard origin/main
git switch feature/功能名称
```

注意：`git reset --hard` 会丢弃当前分支未保存的修改，执行前务必确认工作区状态。

### 13.20 `.env` 文件没有生效

可能原因：

- 文件名写错，例如写成 `.env.txt`。
- 文件放错目录。
- 修改后没有重启服务。

处理方式：

确认文件位置：

```text
apps/web/.env
apps/api/.env
```

修改前端 `.env` 后重启前端：

```bash
npm run dev:web
```

修改后端 `.env` 后重启后端：

```bash
uvicorn app.main:app --reload
```

### 13.21 Docker Compose 全量启动时前端改动不热更新

如果使用：

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

前端会被构建成静态镜像，不会像本地 `npm run dev:web` 那样热更新。

仅前端源码改动后，需要重建 web 镜像：

```bash
docker compose -f deploy/docker-compose.yml up -d --build web
```

日常开发更推荐：

- Docker 只启动 PostgreSQL、Redis、MinIO 等基础服务。
- 后端用 `uvicorn app.main:app --reload` 启动。
- 前端用 `npm run dev:web` 启动。

