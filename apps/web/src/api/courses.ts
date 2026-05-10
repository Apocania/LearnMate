import { request } from "./client";

export type Course = {
  id: number;
  title: string;
  description: string;
  teacher_id: number;
  teacher_name: string;
  status: string;
};

export function listCourses() {
  return request<Course[]>("/courses");
}

export function createCourse(payload: Pick<Course, "title" | "description" | "status">) {
  return request<Course>("/courses", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateCourse(courseId: number, payload: Partial<Pick<Course, "title" | "description" | "status">>) {
  return request<Course>(`/courses/${courseId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function deleteCourse(courseId: number) {
  return request<void>(`/courses/${courseId}`, {
    method: "DELETE"
  });
}
