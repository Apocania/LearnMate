import { request } from "./client";

export type AssistantMessageRequest = {
  content: string;
  course_id?: string;
};

export type AssistantMessageResponse = {
  answer: string;
  citations: Array<{
    document_id: string;
    title: string;
    chunk_index: number;
  }>;
};

export function sendAssistantMessage(payload: AssistantMessageRequest) {
  return request<AssistantMessageResponse>("/assistant/messages", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
