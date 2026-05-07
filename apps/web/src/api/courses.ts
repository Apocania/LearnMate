import { request } from "./client";

export type CourseSummary = {
  id: string;
  title: string;
  description: string;
  teacherName: string;
};

export function listCourses() {
  return request<CourseSummary[]>("/courses");
}

