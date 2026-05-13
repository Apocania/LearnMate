# LearnMate Deploy

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

当前后端课件和头像上传仍写入本地上传目录，MinIO 服务是后续对象存储接入的基础设施预留。
