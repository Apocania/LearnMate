import { clearStoredSession } from "../shared/utils/currentUser";

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() || "/api";
const API_BASE_URL = configuredApiBaseUrl.replace(/\/+$/, "");

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function resolveApiAssetUrl(url?: string | null) {
  if (!url) {
    return undefined;
  }
  if (/^(https?:|data:|blob:)/.test(url)) {
    return url;
  }

  const absoluteBase = API_BASE_URL.startsWith("http")
    ? API_BASE_URL
    : `${window.location.origin}${API_BASE_URL.startsWith("/") ? "" : "/"}${API_BASE_URL}`;
  return new URL(url, absoluteBase).toString();
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem("learnmate_access_token");
  const isFormData = init?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers
    },
    ...init
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // Keep the default message when the response is not JSON.
    }
    if (response.status === 401) {
      clearStoredSession();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  if (!text) {
    return undefined as T;
  }

  return JSON.parse(text) as T;
}
