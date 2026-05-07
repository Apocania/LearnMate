# Guochuang Intelligent Learning Companion

`guochuang` 是一个面向师生教学场景的智能伴学系统平台。

第一版技术栈：

```text
React + TypeScript + Vite
FastAPI
PostgreSQL + pgvector
Redis
MinIO
Docker Compose
```

## Project Structure

```text
apps/web      React 前端应用
apps/api      FastAPI 后端应用
packages      共享类型和工具
docs          项目设计文档
deploy        部署配置
data          示例数据和知识库资料
```

## Development

前端：

```bash
cd apps/web
npm install
npm run dev
```

后端：

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

基础服务：

```bash
cd deploy
docker compose up -d
```

