import { getApiBaseUrl, request } from "./client";
import { clearStoredSession } from "../shared/utils/currentUser";

export type AssistantMessageRequest = {
  content: string;
  course_id?: number | null;
  session_id?: number | null;
  mode?: "qa" | "plan";
};

export type AssistantMessageResponse = {
  session_id?: number | null;
  answer: string;
  citations: Array<{
    document_id: string;
    title: string;
    chunk_index: number;
    snippet: string;
    source_url?: string | null;
  }>;
};

export type AssistantHistoryMessage = {
  id: number;
  role: "assistant" | "user";
  content: string;
  citations: AssistantMessageResponse["citations"];
};

export type AssistantSession = {
  id: number;
  course_id?: number | null;
  title: string;
  messages: AssistantHistoryMessage[];
};

export function listRecentAssistantMessages() {
  return request<AssistantHistoryMessage[]>("/assistant/messages/recent");
}

export function getCurrentAssistantSession(params: { course_id?: number | null; session_id?: number | null } = {}) {
  const query = new URLSearchParams();
  if (params.course_id) {
    query.set("course_id", String(params.course_id));
  }
  if (params.session_id) {
    query.set("session_id", String(params.session_id));
  }
  return request<AssistantSession>(`/assistant/sessions/current${query.size ? `?${query.toString()}` : ""}`);
}

export function createAssistantSession(payload: { course_id?: number | null; title?: string } = {}) {
  return request<AssistantSession>("/assistant/sessions", {
    method: "POST",
    body: JSON.stringify({ title: "新的伴学对话", ...payload })
  });
}

export function sendAssistantMessage(payload: AssistantMessageRequest) {
  return request<AssistantMessageResponse>("/assistant/messages", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

type AssistantStreamEvent =
  | { type: "meta"; session_id?: number | null; citations: AssistantMessageResponse["citations"] }
  | { type: "delta"; content: string }
  | { type: "done" }
  | { type: "error"; message: string };

type AssistantStreamHandlers = {
  onMeta?: (event: Extract<AssistantStreamEvent, { type: "meta" }>) => void;
  onDelta?: (content: string) => void;
  onDone?: () => void;
};

export async function streamAssistantMessage(payload: AssistantMessageRequest, handlers: AssistantStreamHandlers = {}) {
  const token = localStorage.getItem("learnmate_access_token");
  const response = await fetch(`${getApiBaseUrl()}/assistant/messages/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok || !response.body) {
    let message = `请求失败：${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // Keep default message when the stream response is not JSON.
    }
    if (response.status === 401) {
      clearStoredSession();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    throw new Error(message);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.trim()) {
        continue;
      }
      const event = JSON.parse(line) as AssistantStreamEvent;
      if (event.type === "meta") {
        handlers.onMeta?.(event);
      } else if (event.type === "delta") {
        handlers.onDelta?.(event.content);
      } else if (event.type === "done") {
        handlers.onDone?.();
      } else if (event.type === "error") {
        throw new Error(event.message);
      }
    }
  }

  buffer += decoder.decode();
  if (buffer.trim()) {
    const event = JSON.parse(buffer) as AssistantStreamEvent;
    if (event.type === "meta") {
      handlers.onMeta?.(event);
    } else if (event.type === "delta") {
      handlers.onDelta?.(event.content);
    } else if (event.type === "done") {
      handlers.onDone?.();
    } else if (event.type === "error") {
      throw new Error(event.message);
    }
  }
}
