const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export function getApiBaseUrl() {
  return API_BASE_URL;
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
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}
