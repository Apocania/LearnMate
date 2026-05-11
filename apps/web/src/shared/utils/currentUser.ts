import type { CurrentUser } from "../types/user";

export function getStoredCurrentUser(): CurrentUser | null {
  const rawUser = localStorage.getItem("learnmate_current_user");
  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser) as CurrentUser;
  } catch {
    localStorage.removeItem("learnmate_current_user");
    localStorage.removeItem("learnmate_access_token");
    return null;
  }
}

export function clearStoredSession() {
  localStorage.removeItem("learnmate_current_user");
  localStorage.removeItem("learnmate_access_token");
}
