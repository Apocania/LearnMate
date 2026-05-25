# Deployment

更新日期：2026-05-25

本文档用于记录部署方式。

第一版建议使用 Docker Compose 启动：

```text
postgres
redis
minio
api
web/nginx
```

## Local Docker Compose

准备后端环境变量：

```bash
cp deploy/env.example apps/api/.env
```

启动基础服务：

```bash
cd deploy
docker compose up -d postgres redis minio
```

启动全部服务：

```bash
cd deploy
docker compose up -d --build
```

只重建前端静态站点：

```bash
cd deploy
docker compose up -d --build web
```

常用地址：

```text
前端：http://localhost:5173
后端：http://localhost:8000
接口文档：http://localhost:8000/docs
MinIO 控制台：http://localhost:9001
```

## Environment Notes

- `deploy/docker-compose.yml` 会读取 `../apps/api/.env`。
- Docker Compose 场景应使用 `deploy/env.example` 作为模板，因为容器内服务名是 `postgres`、`redis`、`minio`。
- 本机直接运行后端时可使用 `apps/api/.env.example`，其中数据库、Redis、MinIO 地址默认指向 `localhost`。
- 生产环境必须替换 `JWT_SECRET`、数据库密码、MinIO 密钥和大模型 API Key。
- `web` 容器通过 nginx 托管 `npm run build` 后的静态文件，Docker 部署下修改前端源码不会热重载，需要执行 `docker compose up -d --build web`。

## Current Limitations

- 项目已提供 Alembic 初始迁移；开发启动仍保留 `create_all()` 和补丁 SQL 以兼容旧库，生产化时建议收敛到 Alembic 迁移流程。
- 课件上传支持 `STORAGE_BACKEND=local` 和 `STORAGE_BACKEND=minio`；头像和论坛附件仍写入 API 本地目录，需要通过持久化卷或后续对象存储迁移保证可靠性。
- 智能伴学已具备本地检索式回答和 OpenAI 兼容模型接入入口；生产使用前仍建议补充输入限制、限流、内容安全、流式输出和更完整的审计日志。
- 当前前端包含独立创建课程页、学生名单管理、学生学习报告和伴学师教学看板；演示或部署验收时建议分别使用学生和伴学师账号检查角色化页面。

## Demo Data

用于截图或演示时，可以在后端环境运行：

```bash
cd apps/api
.venv/bin/python scripts/seed_demo_data.py
```

演示账号：

```text
demo_student / password123
demo_mentor / password123
```
