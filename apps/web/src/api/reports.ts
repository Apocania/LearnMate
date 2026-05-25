import { request } from "./client";

export type LearningProgressItem = {
  label: string;
  percent: number;
};

export type TeachingCourseSummary = {
  id: number;
  title: string;
  status: string;
  enrollment_count: number;
  chapter_count: number;
  file_count: number;
};

export type MyLearningReport = {
  user_id: number;
  username: string;
  role: "student" | "mentor";
  enrolled_course_count: number;
  created_course_count: number;
  forum_post_count: number;
  forum_comment_count: number;
  ai_question_count: number;
  uploaded_file_count: number;
  learning_event_count: number;
  student_count: number;
  chapter_count: number;
  course_summaries: TeachingCourseSummary[];
  estimated_study_hours: number;
  progress: LearningProgressItem[];
  recent_activities: string[];
  suggestions: string[];
};

export function getMyLearningReports() {
  return request<MyLearningReport>("/reports/me");
}
