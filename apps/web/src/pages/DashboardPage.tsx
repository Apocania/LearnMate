import { PageHeader } from "../components/PageHeader";

export function DashboardPage() {
  return (
    <>
      <PageHeader title="学习首页" description="汇总课程、学习进度、AI 助教和报告入口。" />
      <div className="grid">
        <section className="panel">
          <h3>我的课程</h3>
          <p className="page-description">展示学生已选课程和最近学习记录。</p>
        </section>
        <section className="panel">
          <h3>AI 助教</h3>
          <p className="page-description">提供课程知识问答和学习建议。</p>
        </section>
        <section className="panel">
          <h3>学习报告</h3>
          <p className="page-description">展示学习趋势、互动记录和薄弱知识点。</p>
        </section>
      </div>
    </>
  );
}

