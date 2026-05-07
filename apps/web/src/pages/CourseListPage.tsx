import { PageHeader } from "../components/PageHeader";
import { EmptyState } from "../components/EmptyState";

export function CourseListPage() {
  return (
    <>
      <PageHeader title="课程中心" description="浏览课程、查看详情并完成选课。" />
      <EmptyState title="课程列表待接入" description="后续从 /api/courses 获取课程数据。" />
    </>
  );
}

