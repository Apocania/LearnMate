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

export type CourseChapter = {
  id: number;
  course_id: number;
  title: string;
  description: string;
  sort_order: number;
};

export type CourseEnrollment = {
  id: number;
  course_id: number;
  student_id: number;
  student_name: string;
  created_at: string;
};

export function listCourses() {
  return request<Course[]>("/courses");
}

export function getCourse(courseId: number) {
  return request<Course>(`/courses/${courseId}`);
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

export function listCourseChapters(courseId: number) {
  return request<CourseChapter[]>(`/courses/${courseId}/chapters`);
}

export function createCourseChapter(courseId: number, payload: Pick<CourseChapter, "title" | "description" | "sort_order">) {
  return request<CourseChapter>(`/courses/${courseId}/chapters`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateCourseChapter(
  courseId: number,
  chapterId: number,
  payload: Partial<Pick<CourseChapter, "title" | "description" | "sort_order">>
) {
  return request<CourseChapter>(`/courses/${courseId}/chapters/${chapterId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function deleteCourseChapter(courseId: number, chapterId: number) {
  return request<void>(`/courses/${courseId}/chapters/${chapterId}`, {
    method: "DELETE"
  });
}

export function listCourseEnrollments(courseId: number) {
  return request<CourseEnrollment[]>(`/courses/${courseId}/enrollments`);
}

export function removeCourseEnrollment(courseId: number, enrollmentId: number) {
  return request<void>(`/courses/${courseId}/enrollments/${enrollmentId}`, {
    method: "DELETE"
  });
}
