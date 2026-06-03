wo# LearnMate Deploy

更新日期：2026-05-25

本目录存放 LearnMate 部署相关配置。

第一次使用 Docker Compose 前，请先准备后端环境变量：

```bash
cp env.example ../apps/api/.env
```

然后启动基础服务：

```bash
docker compose up -d postgres redis minio
```

启动全部服务：

```bash
docker compose up -d --build
```

只重建前端：

```bash
docker compose up -d --build web
```

常用地址：

```text
前端：http://localhost:5173
后端：http://localhost:8000
接口文档：http://localhost:8000/docs
MinIO 控制台：http://localhost:9001
```

注意：

- `docker-compose.yml` 会读取 `../apps/api/.env`。
- Compose 环境请优先使用本目录的 `env.example`，其中数据库、Redis、MinIO 地址使用容器服务名。
- 如果从 `apps/api/.env.example` 复制 `.env`，需要确认 `DATABASE_URL`、`REDIS_URL`、`MINIO_ENDPOINT` 是否适合容器网络。
- `web` 服务使用 nginx 托管构建后的静态文件，不是 Vite 开发服务器；修改前端源码后不会热重载，需要重建 `web` 镜像并强刷浏览器。

当前课件上传支持 `STORAGE_BACKEND=local` 和 `STORAGE_BACKEND=minio` 两种模式；头像和论坛附件仍写入 API 容器本地目录。生产部署时建议为 API 容器挂载持久化卷，或后续统一迁移到对象存储。

当前前端已包含独立创建课程页、课程学生名单、学生学习报告和伴学师教学看板。部署验收时建议使用 `demo_student` 与 `demo_mentor` 分别检查学生端和伴学师端页面。

截图展示前可在后端容器或本机后端环境运行：

```bash
cd apps/api
.venv/bin/python scripts/seed_demo_data.py
```
