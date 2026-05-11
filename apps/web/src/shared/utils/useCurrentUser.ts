import { useSyncExternalStore } from "react";

import type { CurrentUser } from "../types/user";
import { getStoredCurrentUser, subscribeToSessionChange } from "./currentUser";

let lastRawUser: string | null = null;
let lastUser: CurrentUser | null = null;

function getCurrentUserSnapshot(): CurrentUser | null {
  const rawUser = localStorage.getItem("learnmate_current_user");
  if (rawUser === lastRawUser) {
    return lastUser;
  }

  lastRawUser = rawUser;
  lastUser = getStoredCurrentUser();
  return lastUser;
}

export function useCurrentUser(): CurrentUser | null {
  return useSyncExternalStore(subscribeToSessionChange, getCurrentUserSnapshot, () => null);
}
