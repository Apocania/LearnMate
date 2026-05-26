from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/status")
def get_system_status() -> dict[str, dict[str, str]]:
  storage_mode = settings.storage_backend.lower().strip() or "local"
  model_status = "已连接" if settings.llm_api_key and settings.llm_base_url and settings.llm_model else "本地兜底"
  return {
    "files": {
      "label": "课件资料",
      "status": "在线",
      "description": "已开启知识库索引",
      "tone": "green",
    },
    "assistant": {
      "label": "智能伴学",
      "status": model_status,
      "description": "可结合课程引用回答",
      "tone": "blue" if model_status == "已连接" else "gold",
    },
    "records": {
      "label": "学习记录",
      "status": "同步",
      "description": "关键学习行为自动沉淀",
      "tone": "gold",
    },
    "storage": {
      "label": "文件存储",
      "status": storage_mode.upper(),
      "description": "当前课件存储模式",
      "tone": "green" if storage_mode == "minio" else "default",
    },
  }
