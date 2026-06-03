from app.core.config import Settings


def test_upload_allowed_types_include_requested_formats() -> None:
  settings = Settings()

  assert settings.is_upload_allowed("slides.ppt", "application/vnd.ms-powerpoint")
  assert settings.is_upload_allowed(
    "slides.pptx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  )
  assert settings.is_upload_allowed("sheet.xls", "application/vnd.ms-excel")
  assert settings.is_upload_allowed(
    "sheet.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )
  assert settings.is_upload_allowed("data.csv", "text/csv")
  assert settings.is_upload_allowed("notes.md", "text/markdown")
  assert settings.is_upload_allowed("image.webp", "image/webp")
  assert settings.is_upload_allowed("archive.zip", "application/zip")
  assert settings.is_upload_allowed("video.mp4", "video/mp4")
  assert settings.is_upload_allowed("legacy.doc", "application/msword")


def test_upload_allowed_extensions_fallback_for_generic_browser_mime() -> None:
  settings = Settings()

  assert settings.is_upload_allowed("slides.pptx", "application/octet-stream")
  assert settings.is_upload_allowed("sheet.xlsx", "application/octet-stream")
  assert settings.is_upload_allowed("archive.zip", "application/octet-stream")
  assert settings.is_upload_allowed("NOTES.MD", "application/octet-stream")


def test_upload_rejects_unknown_type_and_extension() -> None:
  settings = Settings()

  assert not settings.is_upload_allowed("program.exe", "application/octet-stream")
