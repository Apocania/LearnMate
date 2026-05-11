import { request } from "./client";

export type Course = {
  id: number;
  title: string;
  description: string;
  teacher_id: number;
  teacher_name: string;
  status: string;
  enrollment_count: number;
  joined_by_me: boolean;
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

export function enrollCourse(courseId: number) {
  return request<Course>(`/courses/${courseId}/enroll`, {
    method: "POST"
  });
}

export function leaveCourse(courseId: number) {
  return request<Course>(`/courses/${courseId}/enroll`, {
    method: "DELETE"
  });
}
