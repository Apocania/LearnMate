from datetime import datetime

from pydantic import BaseModel


class FileAssetResponse(BaseModel):
  id: int
  original_name: str
  stored_name: str
  content_type: str
  size: int
  uploader_id: int
  uploader_name: str
  created_at: datetime
  url: str

