import { getApiBaseUrl, request } from "./client";

export type FileAsset = {
  id: number;
  original_name: string;
  stored_name: string;
  content_type: string;
  size: number;
  uploader_id: number;
  uploader_name: string;
  created_at: string;
  url: string;
};

export function listFiles() {
  return request<FileAsset[]>("/files");
}

export function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return request<FileAsset>("/files/upload", {
    method: "POST",
    body: formData
  });
}

export function getFileDownloadUrl(file: FileAsset) {
  return `${getApiBaseUrl()}${file.url.replace("/api", "")}`;
}
