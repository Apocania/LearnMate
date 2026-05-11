# Deployment

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
- 本机直接运行后端时可使用 `apps/api/.env.example`，通常数据库地址是 `localhost`。
- 生产环境必须替换 `JWT_SECRET`、数据库密码、MinIO 密钥和大模型 API Key。

## Current Limitations

- 数据库迁移仍未正式 Alembic 化，当前开发阶段依赖 `create_all()` 和少量启动补丁 SQL。
- MinIO 服务已在 Compose 中预留，但文件上传代码仍写入后端本地目录。
- AI 伴学接口已打通，但真实大模型和向量检索仍待接入。
