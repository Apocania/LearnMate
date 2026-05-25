import { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";

const AssistantPage = lazy(() => import("../pages/AssistantPage").then((module) => ({ default: module.AssistantPage })));
const CourseCreatePage = lazy(() => import("../pages/CourseCreatePage").then((module) => ({ default: module.CourseCreatePage })));
const CourseDetailPage = lazy(() => import("../pages/CourseDetailPage").then((module) => ({ default: module.CourseDetailPage })));
const CourseListPage = lazy(() => import("../pages/CourseListPage").then((module) => ({ default: module.CourseListPage })));
const DashboardPage = lazy(() => import("../pages/DashboardPage").then((module) => ({ default: module.DashboardPage })));
const FilesPage = lazy(() => import("../pages/FilesPage").then((module) => ({ default: module.FilesPage })));
const ForumPage = lazy(() => import("../pages/ForumPage").then((module) => ({ default: module.ForumPage })));
const ForumPostEditorPage = lazy(() => import("../pages/ForumPostEditorPage").then((module) => ({ default: module.ForumPostEditorPage })));
const LearningReportPage = lazy(() => import("../pages/LearningReportPage").then((module) => ({ default: module.LearningReportPage })));
const LoginPage = lazy(() => import("../pages/LoginPage").then((module) => ({ default: module.LoginPage })));
const MessagesPage = lazy(() => import("../pages/MessagesPage").then((module) => ({ default: module.MessagesPage })));

function lazyPage(element: React.ReactNode) {
  return <Suspense fallback={<div className="page-loading">页面加载中...</div>}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: lazyPage(<LoginPage />)
  },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: lazyPage(<DashboardPage />) },
      { path: "courses", element: lazyPage(<CourseListPage />) },
      { path: "courses/new", element: lazyPage(<CourseCreatePage />) },
      { path: "courses/:courseId", element: lazyPage(<CourseDetailPage />) },
      { path: "forum", element: lazyPage(<ForumPage />) },
      { path: "forum/new", element: lazyPage(<ForumPostEditorPage />) },
      { path: "files", element: lazyPage(<FilesPage />) },
      { path: "assistant", element: lazyPage(<AssistantPage />) },
      { path: "messages", element: lazyPage(<MessagesPage />) },
      { path: "reports/me", element: lazyPage(<LearningReportPage />) }
    ]
  }
]);
