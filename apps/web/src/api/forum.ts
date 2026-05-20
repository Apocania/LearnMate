import { getApiBaseUrl, request } from "./client";

export type ForumAttachment = {
  original_name: string;
  stored_name: string;
  content_type: string;
  size: number;
  url: string;
};

export type ForumPost = {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_name: string;
  author_avatar_url?: string | null;
  attachments: ForumAttachment[];
  course_id: number | null;
  created_at: string;
  like_count: number;
  comment_count: number;
  liked_by_me: boolean;
};

export type ForumComment = {
  id: number;
  post_id: number;
  author_id: number;
  author_name: string;
  author_avatar_url?: string | null;
  content: string;
  created_at: string;
  can_delete: boolean;
};

export function listPosts() {
  return request<ForumPost[]>("/forum/posts");
}

export function createPost(payload: { title: string; content: string; course_id?: number | null; attachments?: Blob[] }) {
  const formData = new FormData();
  formData.append("title", payload.title);
  formData.append("content", payload.content);
  if (payload.course_id) {
    formData.append("course_id", String(payload.course_id));
  }
  for (const file of payload.attachments ?? []) {
    formData.append("attachments", file);
  }

  return request<ForumPost>("/forum/posts", {
    method: "POST",
    body: formData
  });
}

export function getForumAttachmentDownloadUrl(attachment: ForumAttachment) {
  return `${getApiBaseUrl()}${attachment.url.replace("/api", "")}`;
}

export function listComments(postId: number) {
  return request<ForumComment[]>(`/forum/posts/${postId}/comments`);
}

export function createComment(postId: number, payload: { content: string }) {
  return request<ForumComment>(`/forum/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function deleteComment(commentId: number) {
  return request<void>(`/forum/comments/${commentId}`, {
    method: "DELETE"
  });
}

export function togglePostLike(postId: number) {
  return request<{ liked: boolean; like_count: number }>(`/forum/posts/${postId}/like`, {
    method: "POST"
  });
}

export function deletePost(postId: number) {
  return request<void>(`/forum/posts/${postId}`, {
    method: "DELETE"
  });
}
