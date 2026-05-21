import { getApiBaseUrl, request } from "./client";

export type FileAsset = {
  id: number;
  original_name: string;
  stored_name: string;
  content_type: string;
  size: number;
  course_id?: number | null;
  chapter_id?: number | null;
  storage_provider: string;
  public_url?: string | null;
  uploader_id: number;
  uploader_name: string;
  created_at: string;
  url: string;
};

export function listFiles(params?: { course_id?: number | null; chapter_id?: number | null }) {
  const query = new URLSearchParams();
  if (params?.course_id) {
    query.set("course_id", String(params.course_id));
  }
  if (params?.chapter_id) {
    query.set("chapter_id", String(params.chapter_id));
  }
  return request<FileAsset[]>(`/files${query.size ? `?${query.toString()}` : ""}`);
}

export function uploadFile(file: File, options?: { course_id?: number | null; chapter_id?: number | null }) {
  const formData = new FormData();
  formData.append("file", file);
  if (options?.course_id) {
    formData.append("course_id", String(options.course_id));
  }
  if (options?.chapter_id) {
    formData.append("chapter_id", String(options.chapter_id));
  }

  return request<FileAsset>("/files/upload", {
    method: "POST",
    body: formData
  });
}

export function deleteFile(fileId: number) {
  return request<void>(`/files/${fileId}`, {
    method: "DELETE"
  });
}

export function getFileDownloadUrl(file: FileAsset) {
  return `${getApiBaseUrl()}${file.url.replace("/api", "")}`;
}
