import type { CurrentUser } from "../types/user";

const SESSION_EVENT = "learnmate:session";

function notifySessionChange() {
  window.dispatchEvent(new Event(SESSION_EVENT));
}

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

export function storeSession(accessToken: string, user: CurrentUser) {
  localStorage.setItem("learnmate_access_token", accessToken);
  localStorage.setItem("learnmate_current_user", JSON.stringify(user));
  notifySessionChange();
}

export function updateStoredCurrentUser(user: CurrentUser) {
  localStorage.setItem("learnmate_current_user", JSON.stringify(user));
  notifySessionChange();
}

export function clearStoredSession() {
  localStorage.removeItem("learnmate_current_user");
  localStorage.removeItem("learnmate_access_token");
  notifySessionChange();
}

export function subscribeToSessionChange(callback: () => void) {
  function handleStorage(event: StorageEvent) {
    if (event.key === "learnmate_current_user" || event.key === "learnmate_access_token") {
      callback();
    }
  }

  window.addEventListener(SESSION_EVENT, callback);
  window.addEventListener("storage", handleStorage);

  return () => {
    window.removeEventListener(SESSION_EVENT, callback);
    window.removeEventListener("storage", handleStorage);
  };
}
