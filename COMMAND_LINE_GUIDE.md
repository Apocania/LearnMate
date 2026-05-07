# 智能伴学系统命令行教程与速查表

本文档面向 `guochuang` 智能伴学系统项目，整理开发过程中可能用到的常用命令。项目第一版推荐技术栈是：

```text
React + TypeScript + Vite
FastAPI
PostgreSQL + pgvector
Redis
MinIO
Docker Compose
Git
```

如果你对命令行不熟，建议先掌握前几章：目录导航、文件查看、Git、前端启动、后端启动、Docker Compose。后面的数据库、Redis、排错命令可以边做项目边查。

## 1. 命令行是什么

命令行就是用文字命令操作电脑。开发项目时，经常要用命令行完成这些事情：

- 进入项目目录。
- 查看文件。
- 创建文件夹。
- 安装依赖。
- 启动前端和后端。
- 启动数据库、Redis、MinIO。
- 提交代码。
- 查看日志。
- 排查端口占用。

在本项目中，你经常会在项目根目录执行命令：

```bash
cd /home/apocania/guochuang
```

如果你在 Windows 上开发，常见终端包括 PowerShell、Windows Terminal、Git Bash。本文以 Linux/macOS/bash 写法为主，Windows 用户建议使用 Git Bash 或 WSL。

## 2. 最重要的概念：当前目录

命令通常是在“当前目录”执行的。你必须知道自己现在在哪。

查看当前目录：

```bash
pwd
```

示例输出：

```text
/home/apocania/guochuang
```

这表示你当前在 `guochuang` 项目根目录。

很多错误都是因为命令执行位置不对。例如：

```bash
npm run dev
```

应该在前端目录执行：

```bash
cd apps/web
npm run dev
```

而不是随便在哪个目录都能执行。

## 3. 目录导航命令

进入某个目录：

```bash
cd guochuang
```

进入子目录：

```bash
cd apps/web
```

返回上一级：

```bash
cd ..
```

返回上两级：

```bash
cd ../..
```

回到用户主目录：

```bash
cd ~
```

回到上一次所在目录：

```bash
cd -
```

查看当前目录下有什么：

```bash
ls
```

查看详细信息：

```bash
ls -la
```

查看目录树：

```bash
tree
```

如果没有 `tree`，可以用：

```bash
find . -maxdepth 2 -type d
```

## 4. 文件和文件夹操作

创建文件夹：

```bash
mkdir docs
```

一次创建多层目录：

```bash
mkdir -p apps/web/src
```

创建空文件：

```bash
touch README.md
```

复制文件：

```bash
cp README.md README.backup.md
```

复制文件夹：

```bash
cp -r docs docs-backup
```

移动或重命名文件：

```bash
mv old.md new.md
```

移动文件到目录：

```bash
mv README.md docs/
```

删除文件：

```bash
rm old.md
```

删除空目录：

```bash
rmdir empty-folder
```

删除文件夹及其中所有内容：

```bash
rm -r folder-name
```

注意：`rm` 删除后通常不会进入回收站。不要随便执行：

```bash
rm -rf /
rm -rf *
```

这类命令非常危险。

## 5. 查看文件内容

查看整个文件：

```bash
cat README.md
```

分页查看长文件：

```bash
less README.md
```

在 `less` 中：

```text
空格：下一页
b：上一页
q：退出
/关键词：搜索
```

查看文件前 20 行：

```bash
head -n 20 README.md
```

查看文件后 20 行：

```bash
tail -n 20 README.md
```

实时查看日志：

```bash
tail -f app.log
```

显示行号：

```bash
nl -ba README.md
```

## 6. 搜索命令

搜索文件名：

```bash
find . -name "README.md"
```

搜索所有 Markdown 文件：

```bash
find . -name "*.md"
```

搜索文本内容，推荐使用 `rg`：

```bash
rg "FastAPI"
```

在指定目录搜索：

```bash
rg "login" apps/api
```

显示包含关键词的文件：

```bash
rg -l "Course"
```

忽略大小写：

```bash
rg -i "react"
```

如果没有 `rg`，可以用 `grep`：

```bash
grep -R "FastAPI" .
```

## 7. 命令帮助

查看命令位置：

```bash
which node
which python
which docker
```

查看版本：

```bash
node -v
npm -v
python --version
git --version
docker --version
```

查看命令帮助：

```bash
git --help
npm --help
docker --help
```

查看某个子命令帮助：

```bash
docker compose --help
git commit --help
```

## 8. Git 基础命令

Git 用来管理代码版本。

查看当前仓库状态：

```bash
git status
```

初始化 Git 仓库：

```bash
git init
```

克隆远程仓库：

```bash
git clone https://github.com/your-name/guochuang.git
```

查看提交历史：

```bash
git log
```

简洁查看提交历史：

```bash
git log --oneline
```

查看当前分支：

```bash
git branch
```

创建并切换分支：

```bash
git switch -c feature/login
```

切换分支：

```bash
git switch main
```

添加文件到暂存区：

```bash
git add README.md
```

添加所有改动：

```bash
git add .
```

提交代码：

```bash
git commit -m "Add architecture docs"
```

拉取远程更新：

```bash
git pull
```

推送到远程仓库：

```bash
git push
```

第一次推送新分支：

```bash
git push -u origin feature/login
```

查看具体改了什么：

```bash
git diff
```

查看暂存区改动：

```bash
git diff --staged
```

查看远程仓库：

```bash
git remote -v
```

添加远程仓库：

```bash
git remote add origin https://github.com/your-name/guochuang.git
```

## 9. Git 常见协作流程

开始新功能：

```bash
git switch main
git pull
git switch -c feature/course-list
```

开发后提交：

```bash
git status
git add .
git commit -m "Add course list page"
git push -u origin feature/course-list
```

合并前更新主分支：

```bash
git switch main
git pull
```

查看某个文件的修改：

```bash
git diff apps/web/src/pages/CourseListPage.tsx
```

查看某次提交内容：

```bash
git show commit_id
```

注意：如果你不熟悉 Git，不要轻易执行下面这些命令：

```bash
git reset --hard
git clean -fd
git checkout -- .
```

它们可能丢失本地代码。

## 10. Node.js、npm、pnpm 常用命令

React 前端需要 Node.js。

查看版本：

```bash
node -v
npm -v
```

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

打包前端：

```bash
npm run build
```

预览打包结果：

```bash
npm run preview
```

运行测试：

```bash
npm test
```

运行代码检查：

```bash
npm run lint
```

如果项目使用 pnpm：

```bash
pnpm install
pnpm dev
pnpm build
pnpm test
pnpm lint
```

安装一个前端依赖：

```bash
npm install axios
```

安装开发依赖：

```bash
npm install -D eslint
```

卸载依赖：

```bash
npm uninstall axios
```

## 11. React + Vite 项目命令

进入前端目录：

```bash
cd apps/web
```

安装依赖：

```bash
npm install
```

启动前端：

```bash
npm run dev
```

通常会看到：

```text
Local: http://localhost:5173/
```

打包：

```bash
npm run build
```

预览：

```bash
npm run preview
```

常见前端目录：

```text
apps/web/src/pages
apps/web/src/components
apps/web/src/features
apps/web/src/api
```

如果提示端口被占用，可以换端口：

```bash
npm run dev -- --port 5174
```

## 12. Python 基础命令

FastAPI 后端需要 Python。

查看版本：

```bash
python --version
```

有些系统命令是：

```bash
python3 --version
```

进入 Python 交互环境：

```bash
python
```

退出：

```python
exit()
```

运行 Python 文件：

```bash
python app/main.py
```

## 13. Python 虚拟环境命令

建议后端使用虚拟环境，避免依赖混乱。

进入后端目录：

```bash
cd apps/api
```

创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

退出虚拟环境：

```bash
deactivate
```

安装依赖：

```bash
pip install fastapi uvicorn sqlalchemy alembic pydantic
```

从依赖文件安装：

```bash
pip install -r requirements.txt
```

导出依赖：

```bash
pip freeze > requirements.txt
```

查看已安装包：

```bash
pip list
```

## 14. FastAPI 常用命令

进入后端目录：

```bash
cd apps/api
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

启动开发服务：

```bash
uvicorn app.main:app --reload
```

指定端口：

```bash
uvicorn app.main:app --reload --port 8001
```

允许局域网访问：

```bash
uvicorn app.main:app --reload --host 0.0.0.0
```

接口地址通常是：

```text
http://localhost:8000
```

自动接口文档：

```text
http://localhost:8000/docs
```

备用接口文档：

```text
http://localhost:8000/redoc
```

## 15. Python 测试和格式化

运行测试：

```bash
pytest
```

运行指定测试文件：

```bash
pytest tests/test_auth.py
```

显示更详细输出：

```bash
pytest -v
```

格式化代码：

```bash
black app tests
```

检查代码风格：

```bash
ruff check app tests
```

自动修复部分问题：

```bash
ruff check app tests --fix
```

## 16. 环境变量命令

很多配置不应该写死在代码里，例如数据库地址、AI API Key、JWT 密钥。

临时设置环境变量：

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/guochuang"
```

查看环境变量：

```bash
echo $DATABASE_URL
```

常见 `.env` 文件：

```text
DATABASE_URL=postgresql://user:password@postgres:5432/guochuang
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change-me
LLM_API_KEY=your-api-key
MINIO_ENDPOINT=http://minio:9000
```

查看 `.env`：

```bash
cat .env
```

注意：不要把真实密钥提交到 Git 仓库。

## 17. Docker 基础命令

Docker 用来运行容器。

查看 Docker 版本：

```bash
docker --version
```

查看正在运行的容器：

```bash
docker ps
```

查看所有容器：

```bash
docker ps -a
```

查看镜像：

```bash
docker images
```

查看容器日志：

```bash
docker logs container_name
```

实时查看日志：

```bash
docker logs -f container_name
```

进入容器：

```bash
docker exec -it container_name bash
```

有些容器没有 bash，可以用：

```bash
docker exec -it container_name sh
```

停止容器：

```bash
docker stop container_name
```

启动已停止容器：

```bash
docker start container_name
```

删除容器：

```bash
docker rm container_name
```

删除镜像：

```bash
docker rmi image_name
```

## 18. Docker Compose 常用命令

Docker Compose 用来一次性启动多个服务。

进入部署目录：

```bash
cd deploy
```

启动所有服务：

```bash
docker compose up -d
```

前台启动并查看日志：

```bash
docker compose up
```

停止服务：

```bash
docker compose down
```

查看服务状态：

```bash
docker compose ps
```

查看所有服务日志：

```bash
docker compose logs
```

实时查看日志：

```bash
docker compose logs -f
```

查看某个服务日志：

```bash
docker compose logs -f api
```

重新构建并启动：

```bash
docker compose up -d --build
```

重启某个服务：

```bash
docker compose restart api
```

停止并删除数据卷：

```bash
docker compose down -v
```

注意：`down -v` 会删除数据库、MinIO 等数据卷，可能导致数据丢失。除非明确知道后果，否则不要随便执行。

## 19. PostgreSQL 常用命令

如果 PostgreSQL 用 Docker Compose 启动，可以进入数据库容器：

```bash
docker compose exec postgres psql -U guochuang -d guochuang
```

进入后可以执行 SQL。

查看数据库：

```sql
\l
```

查看表：

```sql
\dt
```

查看表结构：

```sql
\d users
```

查询用户：

```sql
SELECT * FROM users LIMIT 10;
```

退出：

```sql
\q
```

备份数据库：

```bash
pg_dump -U guochuang -d guochuang > backup.sql
```

恢复数据库：

```bash
psql -U guochuang -d guochuang < backup.sql
```

如果使用 Docker：

```bash
docker compose exec postgres pg_dump -U guochuang -d guochuang
```

## 20. Alembic 数据库迁移命令

Alembic 用来管理数据库表结构变更。

进入后端目录：

```bash
cd apps/api
```

初始化 Alembic：

```bash
alembic init migrations
```

生成迁移文件：

```bash
alembic revision --autogenerate -m "create users table"
```

执行迁移：

```bash
alembic upgrade head
```

回滚一个版本：

```bash
alembic downgrade -1
```

查看当前版本：

```bash
alembic current
```

查看迁移历史：

```bash
alembic history
```

## 21. Redis 常用命令

如果 Redis 用 Docker Compose 启动：

```bash
docker compose exec redis redis-cli
```

进入后：

```text
PING
```

返回：

```text
PONG
```

设置 key：

```text
SET test "hello"
```

读取 key：

```text
GET test
```

设置带过期时间的 key：

```text
SETEX captcha:login:001 300 123456
```

查看 key 是否存在：

```text
EXISTS test
```

删除 key：

```text
DEL test
```

查看过期时间：

```text
TTL captcha:login:001
```

查看匹配的 key：

```text
KEYS captcha:*
```

注意：生产环境不要随便使用 `KEYS *`，可能影响性能。

退出：

```text
exit
```

## 22. MinIO 常用操作

MinIO 通常通过网页控制台操作。

常见地址：

```text
http://localhost:9001
```

对象存储 API 地址：

```text
http://localhost:9000
```

常见操作：

- 创建 bucket，例如 `guochuang-materials`。
- 上传课程封面。
- 上传课件 PDF。
- 查看 object key。
- 配置访问权限。

如果安装了 `mc`，可以使用命令行：

```bash
mc alias set local http://localhost:9000 minioadmin minioadmin
```

查看 bucket：

```bash
mc ls local
```

创建 bucket：

```bash
mc mb local/guochuang-materials
```

上传文件：

```bash
mc cp ./course.pdf local/guochuang-materials/course_001/course.pdf
```

下载文件：

```bash
mc cp local/guochuang-materials/course_001/course.pdf ./course.pdf
```

## 23. curl 接口测试命令

`curl` 可以在命令行测试后端 API。

测试后端是否启动：

```bash
curl http://localhost:8000
```

测试健康检查：

```bash
curl http://localhost:8000/api/health
```

发送登录请求：

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"123456"}'
```

携带 token 请求：

```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer your_token"
```

发送 JSON：

```bash
curl -X POST http://localhost:8000/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"title":"机器学习基础","description":"入门课程"}'
```

## 24. 端口和进程排查

前端默认端口：

```text
5173
```

后端默认端口：

```text
8000
```

PostgreSQL 默认端口：

```text
5432
```

Redis 默认端口：

```text
6379
```

MinIO 默认端口：

```text
9000
9001
```

查看端口是否被占用：

```bash
lsof -i :8000
```

如果没有 `lsof`：

```bash
ss -ltnp
```

结束进程：

```bash
kill PID
```

强制结束进程：

```bash
kill -9 PID
```

注意：`kill -9` 比较强硬，优先尝试普通 `kill`。

## 25. 日志查看命令

查看 Docker Compose 日志：

```bash
docker compose logs -f
```

查看后端日志：

```bash
docker compose logs -f api
```

查看数据库日志：

```bash
docker compose logs -f postgres
```

查看 Redis 日志：

```bash
docker compose logs -f redis
```

查看 MinIO 日志：

```bash
docker compose logs -f minio
```

查看本地日志文件：

```bash
tail -f logs/app.log
```

## 26. 常见报错和处理

### 26.1 command not found

示例：

```text
npm: command not found
```

含义：没有安装该工具，或者没有加入 PATH。

处理：

```bash
which npm
npm -v
```

如果命令不存在，需要安装 Node.js。

### 26.2 No such file or directory

示例：

```text
cd apps/web: No such file or directory
```

含义：目录不存在，或者你当前目录不对。

处理：

```bash
pwd
ls
find . -maxdepth 3 -type d
```

### 26.3 Address already in use

示例：

```text
Address already in use
```

含义：端口被占用了。

处理：

```bash
lsof -i :8000
```

换端口：

```bash
uvicorn app.main:app --reload --port 8001
```

### 26.4 Permission denied

示例：

```text
Permission denied
```

含义：权限不足，或文件不可执行。

处理：

```bash
ls -la
chmod +x script.sh
```

不要随便用 `sudo`，先确认为什么没有权限。

### 26.5 ModuleNotFoundError

示例：

```text
ModuleNotFoundError: No module named 'fastapi'
```

含义：Python 依赖没安装，或虚拟环境没激活。

处理：

```bash
source .venv/bin/activate
pip install fastapi
```

### 26.6 npm install 失败

常见处理：

```bash
node -v
npm -v
npm cache verify
npm install
```

如果是网络问题，换网络或配置镜像源。

## 27. 一个完整的本地开发流程

第一次拿到项目：

```bash
git clone https://github.com/your-name/guochuang.git
cd guochuang
```

启动基础服务：

```bash
cd deploy
docker compose up -d
cd ..
```

启动后端：

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

另开一个终端启动前端：

```bash
cd /home/apocania/guochuang/apps/web
npm install
npm run dev
```

访问：

```text
前端：http://localhost:5173
后端：http://localhost:8000
接口文档：http://localhost:8000/docs
MinIO 控制台：http://localhost:9001
```

开发完成后：

```bash
git status
git add .
git commit -m "Implement course list"
git push
```

## 28. 推荐学习顺序

如果你刚开始学命令行，建议按这个顺序掌握：

```text
1. pwd、cd、ls
2. mkdir、touch、cp、mv、rm
3. cat、less、head、tail
4. rg、find
5. git status、git add、git commit、git push、git pull
6. npm install、npm run dev、npm run build
7. python -m venv、source、pip install
8. uvicorn app.main:app --reload
9. docker compose up -d、logs、down
10. psql、redis-cli、curl
```

## 29. 命令速查表

### 29.1 目录与文件

| 目的 | 命令 |
|---|---|
| 查看当前目录 | `pwd` |
| 查看目录内容 | `ls` |
| 查看详细目录内容 | `ls -la` |
| 进入目录 | `cd guochuang` |
| 返回上一级 | `cd ..` |
| 返回主目录 | `cd ~` |
| 创建目录 | `mkdir docs` |
| 创建多层目录 | `mkdir -p apps/web/src` |
| 创建文件 | `touch README.md` |
| 复制文件 | `cp a.md b.md` |
| 复制目录 | `cp -r docs docs-backup` |
| 移动或重命名 | `mv old.md new.md` |
| 删除文件 | `rm old.md` |
| 删除目录 | `rm -r folder` |

### 29.2 查看与搜索

| 目的 | 命令 |
|---|---|
| 查看文件 | `cat README.md` |
| 分页查看 | `less README.md` |
| 查看前 20 行 | `head -n 20 README.md` |
| 查看后 20 行 | `tail -n 20 README.md` |
| 实时查看日志 | `tail -f app.log` |
| 搜索文本 | `rg "keyword"` |
| 搜索文件名 | `find . -name "*.md"` |
| 显示行号 | `nl -ba README.md` |

### 29.3 Git

| 目的 | 命令 |
|---|---|
| 查看状态 | `git status` |
| 初始化仓库 | `git init` |
| 克隆仓库 | `git clone <url>` |
| 查看历史 | `git log --oneline` |
| 查看分支 | `git branch` |
| 新建并切换分支 | `git switch -c feature/name` |
| 切换分支 | `git switch main` |
| 查看改动 | `git diff` |
| 添加改动 | `git add .` |
| 提交 | `git commit -m "message"` |
| 拉取 | `git pull` |
| 推送 | `git push` |
| 推送新分支 | `git push -u origin feature/name` |

### 29.4 React / Node

| 目的 | 命令 |
|---|---|
| 查看 Node 版本 | `node -v` |
| 查看 npm 版本 | `npm -v` |
| 安装依赖 | `npm install` |
| 启动前端 | `npm run dev` |
| 指定端口启动 | `npm run dev -- --port 5174` |
| 打包 | `npm run build` |
| 预览打包结果 | `npm run preview` |
| 安装依赖包 | `npm install axios` |
| 安装开发依赖 | `npm install -D eslint` |

### 29.5 Python / FastAPI

| 目的 | 命令 |
|---|---|
| 查看 Python 版本 | `python --version` |
| 创建虚拟环境 | `python -m venv .venv` |
| 激活虚拟环境 | `source .venv/bin/activate` |
| 退出虚拟环境 | `deactivate` |
| 安装依赖 | `pip install -r requirements.txt` |
| 查看依赖 | `pip list` |
| 启动后端 | `uvicorn app.main:app --reload` |
| 指定端口启动 | `uvicorn app.main:app --reload --port 8001` |
| 运行测试 | `pytest` |
| 格式化代码 | `black app tests` |
| 检查代码 | `ruff check app tests` |

### 29.6 Docker / Docker Compose

| 目的 | 命令 |
|---|---|
| 查看 Docker 版本 | `docker --version` |
| 查看运行中容器 | `docker ps` |
| 查看所有容器 | `docker ps -a` |
| 查看镜像 | `docker images` |
| 查看容器日志 | `docker logs -f container_name` |
| 进入容器 | `docker exec -it container_name bash` |
| 启动所有服务 | `docker compose up -d` |
| 前台启动 | `docker compose up` |
| 停止服务 | `docker compose down` |
| 查看服务状态 | `docker compose ps` |
| 查看日志 | `docker compose logs -f` |
| 查看某服务日志 | `docker compose logs -f api` |
| 重新构建启动 | `docker compose up -d --build` |
| 重启服务 | `docker compose restart api` |

### 29.7 PostgreSQL

| 目的 | 命令 |
|---|---|
| 进入 psql | `docker compose exec postgres psql -U guochuang -d guochuang` |
| 查看数据库 | `\l` |
| 查看表 | `\dt` |
| 查看表结构 | `\d users` |
| 查询数据 | `SELECT * FROM users LIMIT 10;` |
| 退出 psql | `\q` |
| 备份数据库 | `pg_dump -U guochuang -d guochuang > backup.sql` |

### 29.8 Alembic

| 目的 | 命令 |
|---|---|
| 初始化迁移 | `alembic init migrations` |
| 生成迁移 | `alembic revision --autogenerate -m "message"` |
| 执行迁移 | `alembic upgrade head` |
| 回滚一个版本 | `alembic downgrade -1` |
| 查看当前版本 | `alembic current` |
| 查看历史 | `alembic history` |

### 29.9 Redis

| 目的 | 命令 |
|---|---|
| 进入 redis-cli | `docker compose exec redis redis-cli` |
| 测试连接 | `PING` |
| 设置 key | `SET test "hello"` |
| 读取 key | `GET test` |
| 设置过期 key | `SETEX key 300 value` |
| 删除 key | `DEL test` |
| 查看过期时间 | `TTL key` |
| 退出 | `exit` |

### 29.10 MinIO

| 目的 | 命令 |
|---|---|
| 控制台地址 | `http://localhost:9001` |
| API 地址 | `http://localhost:9000` |
| 配置 mc | `mc alias set local http://localhost:9000 minioadmin minioadmin` |
| 查看 bucket | `mc ls local` |
| 创建 bucket | `mc mb local/guochuang-materials` |
| 上传文件 | `mc cp ./file.pdf local/guochuang-materials/file.pdf` |
| 下载文件 | `mc cp local/guochuang-materials/file.pdf ./file.pdf` |

### 29.11 接口测试与排错

| 目的 | 命令 |
|---|---|
| 测试接口 | `curl http://localhost:8000/api/health` |
| POST JSON | `curl -X POST <url> -H "Content-Type: application/json" -d '{}'` |
| 查看端口占用 | `lsof -i :8000` |
| 查看监听端口 | `ss -ltnp` |
| 结束进程 | `kill PID` |
| 强制结束进程 | `kill -9 PID` |
| 查看环境变量 | `echo $DATABASE_URL` |
| 设置环境变量 | `export DATABASE_URL="..."` |

## 30. 最常用的 20 个命令

如果只先记 20 个，建议记这些：

```bash
pwd
ls
ls -la
cd
cd ..
mkdir -p
touch
cat
rg
git status
git add .
git commit -m "message"
git pull
git push
npm install
npm run dev
python -m venv .venv
source .venv/bin/activate
uvicorn app.main:app --reload
docker compose up -d
```

真正做项目时，不需要一次背完所有命令。先知道“要做什么时该查哪一章”，再在实践中慢慢熟悉即可。
