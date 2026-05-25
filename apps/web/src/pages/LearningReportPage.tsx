import { Alert, Card, Col, Progress, Row, Space, Spin, Statistic, Timeline, Typography, message } from "antd";
import { useEffect, useState } from "react";

import { MyLearningReport, getMyLearningReports } from "../api/reports";
import { PageHeader } from "../components/PageHeader";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

export function LearningReportPage() {
  const currentUser = useCurrentUser();
  const [report, setReport] = useState<MyLearningReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function refreshReport() {
    if (!currentUser) {
      setReport(null);
      return;
    }

    setIsLoading(true);
    try {
      setReport(await getMyLearningReports());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "学习报告加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshReport();
  }, [currentUser?.id]);

  if (!currentUser) {
    return (
      <>
        <PageHeader title="个人中心" description="查看学习档案、成长进度和适合你的学习建议。" />
        <Alert message="请先登录后查看个人中心" showIcon type="info" />
      </>
    );
  }

  if (isLoading && !report) {
    return (
      <div className="page-loading">
        <Spin /> 加载学习报告中...
      </div>
    );
  }

  return (
    <>
      <PageHeader title="个人中心" description="查看学习档案、成长进度和适合你的学习建议。" />
      <Row gutter={[16, 16]}>
        <Col lg={6} md={12} xs={24}>
          <Card>
            <Statistic title="估算学习投入" value={report?.estimated_study_hours ?? 0} suffix="小时" />
          </Card>
        </Col>
        <Col lg={6} md={12} xs={24}>
          <Card>
            <Statistic
              title={currentUser.role === "student" ? "已加入课程" : "已创建课程"}
              value={currentUser.role === "student" ? report?.enrolled_course_count ?? 0 : report?.created_course_count ?? 0}
              suffix="门"
            />
          </Card>
        </Col>
        <Col lg={6} md={12} xs={24}>
          <Card>
            <Statistic title="讨论互动" value={(report?.forum_post_count ?? 0) + (report?.forum_comment_count ?? 0)} suffix="次" />
          </Card>
        </Col>
        <Col lg={6} md={12} xs={24}>
          <Card>
            <Statistic title="智能问答/资料" value={`${report?.ai_question_count ?? 0}/${report?.uploaded_file_count ?? 0}`} suffix="次/份" />
          </Card>
        </Col>
      </Row>
      <Row className="section-row" gutter={[16, 16]}>
        <Col lg={12} xs={24}>
          <Card title="能力进度">
            <Space className="progress-list" direction="vertical" size="large">
              {(report?.progress ?? []).map((item) => (
                <div key={item.label}>
                  <Typography.Text>{item.label}</Typography.Text>
                  <Progress percent={item.percent} />
                </div>
              ))}
            </Space>
          </Card>
        </Col>
        <Col lg={12} xs={24}>
          <Card title="学习轨迹">
            <Timeline items={(report?.recent_activities ?? []).map((activity) => ({ children: activity }))} />
          </Card>
        </Col>
      </Row>
      <Card className="section-row" title="学习建议">
        <Space direction="vertical">
          {(report?.suggestions ?? []).map((suggestion) => (
            <Typography.Text key={suggestion}>{suggestion}</Typography.Text>
          ))}
        </Space>
      </Card>
    </>
  );
}
