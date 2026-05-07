# 智能伴学系统服务器迁移部署指南

本文档说明如何把 `guochuang` 智能伴学系统迁移部署到另一台服务器，以及迁移时需要修改哪些配置。

第一版推荐技术栈：

```text
React + TypeScript + Vite
FastAPI
PostgreSQL + pgvector
Redis
MinIO
Docker Compose
Nginx
```

## 1. 先判断你属于哪种迁移

迁移分两种情况。

### 1.1 项目还没有正式数据

如果只是把代码部署到新服务器，还没有真实用户、课程、论坛、课件、学习记录，那么迁移很简单：

```text
1. 新服务器安装 Git、Docker、Docker Compose、Node.js、Python 等环境
2. 拉取代码
3. 修改 .env 配置
4. 启动 Docker Compose
5. 构建前端
6. 启动后端
7. 配置 Nginx 和域名
8. 测试访问
```

### 1.2 已经有正式数据

如果旧服务器已经有数据，需要迁移：

```text
1. 迁移代码
2. 迁移 PostgreSQL 数据库
3. 迁移 MinIO 文件
4. 迁移 Redis 中必要数据，可选
5. 修改新服务器环境变量
6. 修改域名、Nginx、CORS、API 地址
7. 启动服务并验证数据完整性
```

真正重要的数据通常是：

- PostgreSQL 数据库。
- MinIO 中的课件、头像、论坛图片、附件。
- `.env` 中的配置，但不能直接公开。

Redis 大多保存缓存、验证码、限流计数、临时任务状态，通常不需要迁移。

## 2. 迁移前要确认的信息

旧服务器信息：

```text
旧服务器 IP：
旧服务器项目路径：
旧服务器数据库名称：
旧服务器数据库用户名：
旧服务器 MinIO bucket：
旧服务器 Docker Compose 文件位置：
旧服务器 .env 文件位置：
```

新服务器信息：

```text
新服务器 IP：
新服务器系统版本：
新服务器项目路径：
是否有域名：
域名：
是否需要 HTTPS：
```

建议新服务器项目路径：

```text
/opt/guochuang
```

或者：

```text
/home/用户名/guochuang
```

## 3. 哪些内容需要迁移

### 3.1 必须迁移

```text
项目代码
PostgreSQL 数据库
MinIO 文件
.env 配置模板
Nginx 配置
Docker Compose 配置
```

### 3.2 通常不需要迁移

```text
node_modules
.venv
__pycache__
前端 dist，可重新构建
后端日志
Redis 缓存数据
临时文件
```

### 3.3 需要谨慎迁移

```text
.env
JWT_SECRET
LLM_API_KEY
数据库密码
MinIO Access Key
MinIO Secret Key
HTTPS 证书
```

这些都是敏感配置，不建议直接发到聊天软件或提交到 Git 仓库。

## 4. 哪些配置需要修改

迁移到新服务器时，最常改的是这些。

### 4.1 后端环境变量

常见 `.env`：

```text
APP_ENV=production
APP_NAME=guochuang
API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=postgresql://guochuang:password@postgres:5432/guochuang
REDIS_URL=redis://redis:6379/0

JWT_SECRET=change-this-to-a-long-random-secret
JWT_EXPIRE_MINUTES=10080

MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=guochuang-materials

LLM_PROVIDER=openai-compatible
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.example.com/v1
LLM_MODEL=your-model

CORS_ORIGINS=https://your-domain.com
```

需要修改：

- `DATABASE_URL`：数据库地址、用户名、密码、库名。
- `REDIS_URL`：Redis 地址。
- `JWT_SECRET`：生产环境必须换成强随机字符串。
- `MINIO_ENDPOINT`：如果容器内访问通常是 `http://minio:9000`，如果外部访问可能是域名。
- `MINIO_ACCESS_KEY` 和 `MINIO_SECRET_KEY`：生产环境不要用默认值。
- `LLM_API_KEY`：新服务器需要配置。
- `CORS_ORIGINS`：改成新域名或新 IP。

### 4.2 前端环境变量

React + Vite 常见 `.env.production`：

```text
VITE_API_BASE_URL=https://your-domain.com/api
VITE_APP_NAME=智能伴学系统
```

如果没有域名，只用 IP：

```text
VITE_API_BASE_URL=http://new-server-ip:8000/api
```

如果使用 Nginx 反向代理，推荐：

```text
VITE_API_BASE_URL=https://your-domain.com/api
```

需要修改：

- `VITE_API_BASE_URL`
- 所有写死的旧服务器 IP
- 所有写死的旧域名

可以搜索旧 IP 或旧域名：

```bash
rg "旧服务器IP"
rg "旧域名"
```

### 4.3 Nginx 配置

常见 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /opt/guochuang/apps/web/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

需要修改：

- `server_name`
- `root`
- `proxy_pass`
- HTTPS 证书路径，如果配置了 HTTPS

### 4.4 Docker Compose 配置

常见需要改：

- 服务端口映射。
- 数据卷路径。
- 环境变量文件路径。
- 镜像名称。
- 容器名称。
- 网络名称。

示例：

```yaml
services:
  api:
    env_file:
      - ../apps/api/.env
    ports:
      - "8000:8000"

  postgres:
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    ports:
      - "6379:6379"

  minio:
    ports:
      - "9000:9000"
      - "9001:9001"
```

如果新服务器已有服务占用端口，需要改端口映射。例如：

```yaml
ports:
  - "8001:8000"
```

表示服务器外部访问 `8001`，容器内部仍然是 `8000`。

## 5. 新服务器基础环境准备

登录新服务器：

```bash
ssh username@new-server-ip
```

更新系统：

```bash
sudo apt update
sudo apt upgrade
```

安装常用工具：

```bash
sudo apt install -y git curl vim unzip nginx
```

安装 Docker 后检查：

```bash
docker --version
docker compose version
```

如果使用非 root 用户运行 Docker，需要把用户加入 docker 组：

```bash
sudo usermod -aG docker $USER
```

然后重新登录服务器。

## 6. 迁移代码

推荐方式是从 Git 仓库拉取：

```bash
cd /opt
sudo git clone https://github.com/your-name/guochuang.git
sudo chown -R $USER:$USER /opt/guochuang
cd /opt/guochuang
```

如果还没有远程 Git 仓库，可以从旧服务器打包复制：

旧服务器：

```bash
cd /path/to
tar -czf guochuang-code.tar.gz guochuang
scp guochuang-code.tar.gz username@new-server-ip:/opt/
```

新服务器：

```bash
cd /opt
tar -xzf guochuang-code.tar.gz
```

不建议迁移：

```text
node_modules
.venv
dist
__pycache__
```

这些可以在新服务器重新生成。

## 7. 迁移 PostgreSQL 数据

### 7.1 从旧服务器备份数据库

如果 PostgreSQL 在 Docker Compose 里：

```bash
cd /path/to/guochuang/deploy
docker compose exec postgres pg_dump -U guochuang -d guochuang > guochuang_backup.sql
```

如果 PostgreSQL 直接装在服务器上：

```bash
pg_dump -U guochuang -d guochuang > guochuang_backup.sql
```

压缩备份：

```bash
gzip guochuang_backup.sql
```

复制到新服务器：

```bash
scp guochuang_backup.sql.gz username@new-server-ip:/opt/guochuang/
```

### 7.2 在新服务器恢复数据库

启动新服务器数据库：

```bash
cd /opt/guochuang/deploy
docker compose up -d postgres
```

解压：

```bash
cd /opt/guochuang
gunzip guochuang_backup.sql.gz
```

恢复：

```bash
cd /opt/guochuang/deploy
docker compose exec -T postgres psql -U guochuang -d guochuang < ../guochuang_backup.sql
```

检查表：

```bash
docker compose exec postgres psql -U guochuang -d guochuang
```

进入后执行：

```sql
\dt
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM courses;
\q
```

## 8. 迁移 pgvector

如果 pgvector 装在 PostgreSQL 里，通常跟随 PostgreSQL 数据库一起迁移。

但新服务器的 PostgreSQL 镜像或数据库必须支持 pgvector 扩展。

检查扩展：

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

如果没有，需要创建：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

注意：如果新服务器使用的 PostgreSQL 镜像不带 pgvector，需要换成支持 pgvector 的镜像，或者手动安装扩展。

## 9. 迁移 MinIO 文件

MinIO 保存课件、头像、论坛图片、附件，是必须迁移的。

### 9.1 使用 mc 迁移

在一台能同时访问旧 MinIO 和新 MinIO 的机器上：

```bash
mc alias set old http://old-server-ip:9000 old_access_key old_secret_key
mc alias set new http://new-server-ip:9000 new_access_key new_secret_key
```

查看 bucket：

```bash
mc ls old
mc ls new
```

创建新 bucket：

```bash
mc mb new/guochuang-materials
```

同步文件：

```bash
mc mirror old/guochuang-materials new/guochuang-materials
```

### 9.2 使用数据卷迁移

如果 MinIO 数据存在 Docker volume 中，也可以备份数据卷。但对初学者更推荐使用 `mc mirror`。

迁移后要检查：

- 课程封面能否打开。
- 课件是否能下载。
- 论坛图片是否能显示。
- AI 知识库对应的原文文件是否存在。

## 10. Redis 需要迁移吗

通常不需要。

Redis 中常见数据：

- 登录验证码。
- 限流计数。
- 临时 token。
- 热点缓存。
- 后台任务状态。

这些通常可以丢弃，系统启动后会重新生成。

如果 Redis 中保存了重要任务队列，而且旧服务器还有未完成的课件解析任务，建议迁移前先：

```text
1. 暂停用户上传
2. 等待任务处理完成
3. 再迁移 PostgreSQL 和 MinIO
```

## 11. 构建和启动新服务器服务

### 11.1 准备环境变量

复制模板：

```bash
cp deploy/env.example apps/api/.env
```

编辑：

```bash
vim apps/api/.env
```

至少确认：

```text
DATABASE_URL
REDIS_URL
JWT_SECRET
MINIO_ENDPOINT
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
MINIO_BUCKET
LLM_API_KEY
CORS_ORIGINS
```

### 11.2 启动基础服务

```bash
cd /opt/guochuang/deploy
docker compose up -d postgres redis minio
```

检查：

```bash
docker compose ps
docker compose logs -f postgres
```

### 11.3 执行数据库迁移

如果你是从空数据库开始：

```bash
cd /opt/guochuang/apps/api
source .venv/bin/activate
alembic upgrade head
```

如果你是恢复旧数据库：

```bash
alembic current
alembic upgrade head
```

### 11.4 启动后端

开发式启动：

```bash
cd /opt/guochuang/apps/api
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

生产环境更建议用 Docker Compose 或 systemd 管理。第一版可以先使用 Docker Compose。

### 11.5 构建前端

```bash
cd /opt/guochuang/apps/web
npm install
npm run build
```

生成目录：

```text
apps/web/dist
```

Nginx 应该指向这个目录。

## 12. 配置 Nginx

创建配置：

```bash
sudo vim /etc/nginx/sites-available/guochuang
```

示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /opt/guochuang/apps/web/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /minio/ {
        proxy_pass http://127.0.0.1:9000/;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/guochuang /etc/nginx/sites-enabled/guochuang
```

检查配置：

```bash
sudo nginx -t
```

重载 Nginx：

```bash
sudo systemctl reload nginx
```

如果没有域名，可以临时使用：

```nginx
server_name _;
```

然后通过：

```text
http://new-server-ip
```

访问。

## 13. 配置 HTTPS

如果有域名，建议使用 HTTPS。

常见方式是 Certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

证书自动续期检查：

```bash
sudo certbot renew --dry-run
```

如果没有域名，先不要强行配置 HTTPS，可以先用 HTTP 测试。

## 14. 防火墙和安全组

云服务器通常有两层防火墙：

```text
服务器系统防火墙
云厂商安全组
```

常见需要开放：

```text
22    SSH
80    HTTP
443   HTTPS
```

开发调试时可能临时开放：

```text
8000  FastAPI
5173  Vite
9001  MinIO 控制台
```

生产环境不建议直接暴露：

```text
5432  PostgreSQL
6379  Redis
9000  MinIO API
```

建议让 Nginx 统一对外服务，数据库和 Redis 只在服务器内部或 Docker 网络内访问。

如果使用 ufw：

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status
```

## 15. CORS 跨域配置

如果前端地址和后端地址不同，就可能遇到跨域问题。

例如：

```text
前端：http://new-server-ip:5173
后端：http://new-server-ip:8000
```

需要在后端允许前端来源：

```text
CORS_ORIGINS=http://new-server-ip:5173,http://new-server-ip
```

如果使用统一域名和 Nginx：

```text
前端：https://your-domain.com
后端：https://your-domain.com/api
```

跨域问题会少很多。

不要在生产环境随便配置：

```text
CORS_ORIGINS=*
```

这会降低安全性。

## 16. AI 大模型配置迁移

迁移后需要检查：

```text
LLM_PROVIDER
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL
EMBEDDING_MODEL
```

如果 AI 服务提供商限制 IP 白名单，需要把新服务器 IP 加入白名单。

如果使用本地模型，还需要迁移：

- 模型文件。
- 推理服务配置。
- GPU 驱动。
- CUDA 环境。
- 模型服务端口。

第一版如果使用外部大模型 API，只需要正确设置 API Key、Base URL、模型名即可。

## 17. 迁移后的检查清单

### 17.1 基础服务检查

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f minio
```

### 17.2 后端检查

```bash
curl http://127.0.0.1:8000/api/health
```

浏览器访问：

```text
http://new-server-ip:8000/docs
```

### 17.3 前端检查

访问：

```text
http://new-server-ip
```

检查：

- 页面是否能打开。
- 登录是否正常。
- 前端是否调用了旧服务器 API。
- 控制台是否有跨域错误。

### 17.4 数据检查

进入数据库：

```bash
docker compose exec postgres psql -U guochuang -d guochuang
```

检查：

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM courses;
SELECT COUNT(*) FROM forum_posts;
SELECT COUNT(*) FROM course_materials;
```

### 17.5 文件检查

检查：

- 头像是否显示。
- 课程封面是否显示。
- 课件是否能下载。
- MinIO bucket 是否存在。
- 文件 object key 是否和数据库中保存的一致。

### 17.6 AI 检查

检查：

- AI 助教能否回答普通问题。
- AI 助教能否基于课程资料回答。
- embedding 是否能生成。
- pgvector 扩展是否可用。
- 大模型 API 是否报错。

## 18. 常见问题

### 18.1 前端还在请求旧服务器

原因：

- `VITE_API_BASE_URL` 没改。
- 前端打包后没有重新部署。
- 代码里写死了旧 IP。

处理：

```bash
rg "旧服务器IP" apps/web
rg "旧域名" apps/web
```

修改后重新构建：

```bash
cd apps/web
npm run build
sudo systemctl reload nginx
```

### 18.2 后端连不上数据库

检查：

```bash
echo $DATABASE_URL
docker compose ps
docker compose logs postgres
```

如果后端和 PostgreSQL 都在 Docker Compose 内，数据库主机名通常是服务名：

```text
postgres
```

而不是：

```text
localhost
```

### 18.3 MinIO 文件打不开

检查：

- `MINIO_ENDPOINT` 是否正确。
- bucket 是否存在。
- object key 是否正确。
- Nginx 是否代理了文件访问。
- 文件访问权限是否允许。

### 18.4 登录后立刻失效

检查：

- `JWT_SECRET` 是否和旧服务器一致。
- token 过期时间是否配置太短。
- 前后端时间是否差异太大。

如果要让旧 token 在新服务器继续有效，需要保持同一个 `JWT_SECRET`。如果希望所有用户重新登录，可以更换 `JWT_SECRET`。

### 18.5 AI 问答失败

检查：

- `LLM_API_KEY` 是否配置。
- 新服务器 IP 是否被服务商允许。
- `LLM_BASE_URL` 是否正确。
- 服务器是否能访问外网。
- 模型名是否正确。
- embedding 模型是否可用。

### 18.6 跨域错误

浏览器控制台如果出现 CORS 错误，检查：

- 后端 `CORS_ORIGINS`
- 前端 `VITE_API_BASE_URL`
- Nginx 代理路径
- HTTP 和 HTTPS 是否混用

## 19. 迁移推荐顺序

如果项目已有线上数据，推荐按这个顺序：

```text
1. 选定新服务器目录和域名
2. 在新服务器安装 Docker、Nginx、Git
3. 拉取代码
4. 配置 .env
5. 启动 PostgreSQL、Redis、MinIO
6. 备份旧 PostgreSQL
7. 恢复到新 PostgreSQL
8. 迁移 MinIO bucket 文件
9. 检查 pgvector 扩展
10. 构建前端
11. 启动后端
12. 配置 Nginx
13. 配置 HTTPS
14. 修改 DNS 解析到新服务器
15. 全功能检查
16. 保留旧服务器一段时间，确认稳定后再下线
```

如果项目还没有正式数据，顺序可以简化：

```text
1. 新服务器安装 Docker、Nginx、Git
2. 拉取代码
3. 配置 .env
4. docker compose up -d
5. npm run build
6. 启动后端
7. 配置 Nginx
8. 测试访问
```

## 20. 修改项速查表

| 类型 | 需要修改的内容 | 示例 |
|---|---|---|
| 前端 API 地址 | `VITE_API_BASE_URL` | `https://your-domain.com/api` |
| 后端跨域 | `CORS_ORIGINS` | `https://your-domain.com` |
| 数据库连接 | `DATABASE_URL` | `postgresql://user:pass@postgres:5432/db` |
| Redis 连接 | `REDIS_URL` | `redis://redis:6379/0` |
| JWT 密钥 | `JWT_SECRET` | 生产环境强随机字符串 |
| MinIO 地址 | `MINIO_ENDPOINT` | `http://minio:9000` |
| MinIO 账号 | `MINIO_ACCESS_KEY` | 不要用默认值 |
| MinIO 密码 | `MINIO_SECRET_KEY` | 不要用默认值 |
| MinIO bucket | `MINIO_BUCKET` | `guochuang-materials` |
| 大模型 Key | `LLM_API_KEY` | 新服务器需要配置 |
| 大模型地址 | `LLM_BASE_URL` | 模型服务商 API 地址 |
| Nginx 域名 | `server_name` | `your-domain.com` |
| Nginx 前端目录 | `root` | `/opt/guochuang/apps/web/dist` |
| Nginx 后端代理 | `proxy_pass` | `http://127.0.0.1:8000/api/` |
| Docker 端口 | `ports` | `"8000:8000"` |
| 防火墙 | 端口开放 | `22`、`80`、`443` |
| DNS | 域名 A 记录 | 指向新服务器 IP |

## 21. 数据迁移速查表

| 数据 | 是否必须迁移 | 迁移方式 |
|---|---:|---|
| 项目代码 | 是 | Git clone 或 tar + scp |
| PostgreSQL | 有正式数据时必须 | `pg_dump` + `psql` |
| pgvector 数据 | 是 | 跟随 PostgreSQL 迁移 |
| MinIO 文件 | 有上传文件时必须 | `mc mirror` |
| Redis | 通常否 | 一般重新生成 |
| node_modules | 否 | 新服务器 `npm install` |
| Python .venv | 否 | 新服务器重新创建 |
| 前端 dist | 否 | 新服务器重新 `npm run build` |
| 日志文件 | 否 | 可按需归档 |
| `.env` | 需要重建 | 参考旧配置手动填写 |

## 22. 最小迁移命令示例

以下是假设代码已有 Git 仓库、数据还不重要的最小部署流程：

```bash
ssh username@new-server-ip
cd /opt
git clone https://github.com/your-name/guochuang.git
cd guochuang
cp deploy/env.example apps/api/.env
vim apps/api/.env
cd deploy
docker compose up -d
cd ../apps/web
npm install
npm run build
cd ../../
sudo nginx -t
sudo systemctl reload nginx
```

如果有正式数据，请先备份旧服务器数据库和 MinIO 文件，再切换域名。不要在没有备份的情况下直接停旧服务器。
