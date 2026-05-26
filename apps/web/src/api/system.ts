import { request } from "./client";

export type SystemStatusItem = {
  label: string;
  status: string;
  description: string;
  tone: "green" | "blue" | "gold" | "default";
};

export type SystemStatus = Record<string, SystemStatusItem>;

export function getSystemStatus() {
  return request<SystemStatus>("/system/status");
}
