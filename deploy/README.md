# Deploy

本目录存放部署相关配置。

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

