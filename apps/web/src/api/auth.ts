import { request } from "./client";
import type { CurrentUser, UserRole } from "../shared/types/user";

export type RegisterRequest = {
  username: string;
  password: string;
  role: UserRole;
};

export type LoginRequest = {
  username: string;
  password: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: CurrentUser;
};

export function register(payload: RegisterRequest) {
  return request<LoginResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function login(payload: LoginRequest) {
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getCurrentUser() {
  return request<CurrentUser>("/users/me");
}
