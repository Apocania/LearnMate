import { request } from "./client";

export function getMyLearningReports() {
  return request("/reports/me");
}

