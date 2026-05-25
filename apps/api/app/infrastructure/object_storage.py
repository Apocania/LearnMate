from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.core.config import settings


LOCAL_STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "uploads"


class StoredObject:
  def __init__(self, provider: str, object_key: str, public_url: str | None = None) -> None:
    self.provider = provider
    self.object_key = object_key
    self.public_url = public_url


class ObjectStorageClient:
  def __init__(self) -> None:
    self.backend = settings.storage_backend.lower().strip() or "local"
    LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

  def put_object(self, object_key: str, data: bytes, content_type: str) -> StoredObject:
    object_key = self._normalize_object_key(object_key)
    if self.backend == "minio":
      return self._put_minio_object(object_key, data, content_type)
    return self._put_local_object(object_key, data)

  def get_local_path(self, object_key: str) -> Path:
    object_key = self._normalize_object_key(object_key)
    path = (LOCAL_STORAGE_DIR / object_key).resolve()
    if LOCAL_STORAGE_DIR.resolve() not in path.parents and path != LOCAL_STORAGE_DIR.resolve():
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件路径无效")
    if not path.exists():
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件已丢失")
    return path

  def read_object(self, object_key: str, provider: str | None = None) -> bytes:
    object_key = self._normalize_object_key(object_key)
    if (provider or self.backend) == "minio":
      client = self._create_minio_client()
      try:
        response = client.get_object(settings.minio_bucket, object_key)
        try:
          return response.read()
        finally:
          response.close()
          response.release_conn()
      except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件已丢失") from exc
    return self.get_local_path(object_key).read_bytes()

  def delete_object(self, object_key: str, provider: str | None = None) -> None:
    object_key = self._normalize_object_key(object_key)
    if (provider or self.backend) == "minio":
      client = self._create_minio_client()
      client.remove_object(settings.minio_bucket, object_key)
      return
    path = LOCAL_STORAGE_DIR / object_key
    path.unlink(missing_ok=True)

  def _put_local_object(self, object_key: str, data: bytes) -> StoredObject:
    path = LOCAL_STORAGE_DIR / object_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return StoredObject(provider="local", object_key=object_key)

  def _put_minio_object(self, object_key: str, data: bytes, content_type: str) -> StoredObject:
    from io import BytesIO

    client = self._create_minio_client()
    bucket = settings.minio_bucket
    if not client.bucket_exists(bucket):
      client.make_bucket(bucket)
    client.put_object(bucket, object_key, BytesIO(data), length=len(data), content_type=content_type)
    return StoredObject(
      provider="minio",
      object_key=object_key,
      public_url=f"{settings.minio_endpoint.rstrip('/')}/{bucket}/{object_key}",
    )

  def _create_minio_client(self):
    try:
      from minio import Minio
    except ImportError as exc:
      raise RuntimeError("storage_backend=minio 需要安装 minio 依赖") from exc

    parsed = urlparse(settings.minio_endpoint)
    endpoint = parsed.netloc or parsed.path
    secure = parsed.scheme == "https"
    return Minio(
      endpoint,
      access_key=settings.minio_access_key,
      secret_key=settings.minio_secret_key,
      secure=secure,
    )

  def _normalize_object_key(self, object_key: str) -> str:
    if "\\" in object_key:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件路径无效")
    path = Path(object_key)
    if path.is_absolute() or ".." in path.parts:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件路径无效")
    normalized = path.as_posix().lstrip("/")
    if not normalized:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件路径无效")
    return normalized
