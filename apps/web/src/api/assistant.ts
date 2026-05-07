import { request } from "./client";

export type AssistantMessageRequest = {
  content: string;
  courseId?: string;
};

export function sendAssistantMessage(payload: AssistantMessageRequest) {
  return request("/assistant/messages", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

