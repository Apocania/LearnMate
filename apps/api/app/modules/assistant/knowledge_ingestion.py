import re
import hashlib
import json
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree

from sqlalchemy.orm import Session

from app.modules.assistant.models import KnowledgeChunk
from app.modules.assistant.repository import AssistantRepository
from app.modules.files.models import FileAsset

MAX_CHUNK_CHARS = 900
CHUNK_OVERLAP_CHARS = 120
EMBEDDING_DIMENSION = 64


class KnowledgeIngestionService:
  def __init__(self, db: Session) -> None:
    self.repository = AssistantRepository(db)

  def ingest_file(self, file_asset: FileAsset, data: bytes) -> int:
    text = self._extract_text(file_asset, data)
    self.repository.delete_chunks_for_file(file_asset.id)
    if not text.strip():
      return 0

    chunks = [
      KnowledgeChunk(
        file_asset_id=file_asset.id,
        course_id=file_asset.course_id,
        chapter_id=file_asset.chapter_id,
        document_id=f"file:{file_asset.id}",
        title=file_asset.original_name,
        chunk_index=index,
        content=chunk,
        keywords=" ".join(self._keywords(chunk)),
        embedding=json.dumps(self._embed(chunk)),
        source_url=f"/api/files/{file_asset.id}/download",
      )
      for index, chunk in enumerate(self._split_text(text), start=1)
    ]
    self.repository.create_chunks(chunks)
    return len(chunks)

  def remove_file_chunks(self, file_asset_id: int) -> int:
    return self.repository.delete_chunks_for_file(file_asset_id)

  def _extract_text(self, file_asset: FileAsset, data: bytes) -> str:
    content_type = file_asset.content_type.lower()
    file_name = file_asset.original_name.lower()
    if content_type.startswith("text/") or file_name.endswith((".md", ".txt", ".csv")):
      return data.decode("utf-8", errors="ignore")
    if content_type == "application/pdf" or file_name.endswith(".pdf"):
      return self._extract_pdf_text(data)
    if content_type.endswith("wordprocessingml.document") or file_name.endswith(".docx"):
      return self._extract_docx_text(data)
    return ""

  def _extract_pdf_text(self, data: bytes) -> str:
    try:
      from pypdf import PdfReader
    except ImportError:
      return ""

    reader = PdfReader(BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)

  def _extract_docx_text(self, data: bytes) -> str:
    try:
      with ZipFile(BytesIO(data)) as archive:
        xml = archive.read("word/document.xml")
    except Exception:
      return ""

    root = ElementTree.fromstring(xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{namespace}p"):
      texts = [node.text or "" for node in paragraph.iter(f"{namespace}t")]
      if texts:
        paragraphs.append("".join(texts))
    return "\n".join(paragraphs)

  def _split_text(self, text: str) -> list[str]:
    normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(normalized) <= MAX_CHUNK_CHARS:
      return [normalized]

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
      end = min(start + MAX_CHUNK_CHARS, len(normalized))
      breakpoint = normalized.rfind("\n", start, end)
      if breakpoint <= start + 200:
        breakpoint = normalized.rfind("。", start, end)
      if breakpoint <= start + 200:
        breakpoint = end
      chunk = normalized[start:breakpoint].strip()
      if chunk:
        chunks.append(chunk)
      if breakpoint >= len(normalized):
        break
      start = max(breakpoint - CHUNK_OVERLAP_CHARS, start + 1)
    return chunks

  def _keywords(self, text: str) -> list[str]:
    words = re.findall(r"[\w\u4e00-\u9fff]{2,}", text.lower())
    seen: set[str] = set()
    keywords: list[str] = []
    for word in words:
      if word in seen:
        continue
      seen.add(word)
      keywords.append(word)
      if len(keywords) >= 30:
        break
    return keywords

  def _embed(self, text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    tokens = self._keywords(text)
    for token in tokens:
      digest = hashlib.sha256(token.encode("utf-8")).digest()
      index = int.from_bytes(digest[:2], "big") % EMBEDDING_DIMENSION
      sign = 1.0 if digest[2] % 2 == 0 else -1.0
      vector[index] += sign
    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0:
      return vector
    return [round(value / norm, 6) for value in vector]
