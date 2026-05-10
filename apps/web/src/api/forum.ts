import { request } from "./client";

export type ForumPost = {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_name: string;
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
  content: string;
  created_at: string;
};

export function listPosts() {
  return request<ForumPost[]>("/forum/posts");
}

export function createPost(payload: { title: string; content: string; course_id?: number | null }) {
  return request<ForumPost>("/forum/posts", {
    method: "POST",
    body: JSON.stringify(payload)
  });
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

export function togglePostLike(postId: number) {
  return request<{ liked: boolean; like_count: number }>(`/forum/posts/${postId}/like`, {
    method: "POST"
  });
}
