# API

FastAPI 后端应用。

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

访问：

```text
http://localhost:8000/api/health
http://localhost:8000/docs
```

