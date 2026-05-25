export function formatCourseStatus(status: string) {
  if (status === "published") {
    return "已发布";
  }
  if (status === "draft") {
    return "草稿";
  }
  return status;
}

export function formatStorageProvider(provider: string) {
  if (provider === "local") {
    return "本地存储";
  }
  if (provider === "minio") {
    return "对象存储";
  }
  return provider;
}

export function formatContentType(contentType: string) {
  const labels: Record<string, string> = {
    "application/pdf": "便携文档",
    "application/msword": "Word 文档",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word 文档",
    "image/jpeg": "图片",
    "image/png": "图片",
    "image/gif": "动图",
    "image/webp": "图片",
    "text/markdown": "标记文本",
    "text/plain": "纯文本"
  };
  return labels[contentType] ?? contentType;
}
