import { request } from "./client";

export function listPosts() {
  return request("/forum/posts");
}

