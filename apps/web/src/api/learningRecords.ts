import { request } from "./client";

export type CourseProgressUpdate = {
  course_id: number;
  progress_percent: number;
  study_seconds_delta: number;
  last_position?: string;
};

export type CourseProgress = {
  id: number;
  user_id: number;
  course_id: number;
  progress_percent: number;
  study_seconds: number;
  last_position: string;
  created_at: string;
  updated_at: string;
};

export function updateCourseProgress(payload: CourseProgressUpdate) {
  return request<CourseProgress>("/learning-records/course-progress", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
