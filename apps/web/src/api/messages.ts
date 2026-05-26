import { request } from "./client";

export type UserMessageType = "like" | "comment" | "private" | "announcement";

export type UserMessage = {
  id: number;
  recipient_id: number;
  recipient_name: string;
  sender_id: number | null;
  sender_name: string | null;
  message_type: UserMessageType;
  title: string;
  content: string;
  source_type: string | null;
  source_id: number | null;
  is_read: boolean;
  created_at: string;
};

export type StudentRecipient = {
  id: number;
  username: string;
  avatar_url?: string | null;
  course_id: number;
  course_title: string;
};

export function listMessages() {
  return request<UserMessage[]>("/messages");
}

export function getUnreadMessageCount() {
  return request<{ unread_count: number }>("/messages/unread-count");
}

export function markMessageAsRead(messageId: number) {
  return request<UserMessage>(`/messages/${messageId}/read`, {
    method: "POST"
  });
}

export function markAllMessagesAsRead() {
  return request<void>("/messages/read-all", {
    method: "POST"
  });
}

export function listStudentRecipients() {
  return request<StudentRecipient[]>("/messages/student-recipients");
}

export function sendPrivateMessage(payload: { course_id: number; recipient_username: string; title: string; content: string }) {
  return request<UserMessage>("/messages/private", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function sendAnnouncement(payload: { course_id: number; title: string; content: string }) {
  return request<{ created_count: number }>("/messages/announcements", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
