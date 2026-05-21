import { request } from "./client";

export type AssistantMessageRequest = {
  content: string;
  course_id?: number | null;
  session_id?: number | null;
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

export function sendAssistantMessage(payload: AssistantMessageRequest) {
  return request<AssistantMessageResponse>("/assistant/messages", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
