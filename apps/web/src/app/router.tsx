import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { AssistantPage } from "../pages/AssistantPage";
import { CourseDetailPage } from "../pages/CourseDetailPage";
import { CourseListPage } from "../pages/CourseListPage";
import { DashboardPage } from "../pages/DashboardPage";
import { ForumPage } from "../pages/ForumPage";
import { FilesPage } from "../pages/FilesPage";
import { LearningReportPage } from "../pages/LearningReportPage";
import { LoginPage } from "../pages/LoginPage";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />
  },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "courses", element: <CourseListPage /> },
      { path: "courses/:courseId", element: <CourseDetailPage /> },
      { path: "forum", element: <ForumPage /> },
      { path: "files", element: <FilesPage /> },
      { path: "assistant", element: <AssistantPage /> },
      { path: "reports/me", element: <LearningReportPage /> }
    ]
  }
]);
