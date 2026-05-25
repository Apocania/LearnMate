import {
  Alert,
  Button,
  Card,
  Col,
  List,
  Progress,
  Row,
  Space,
  Spin,
  Statistic,
  Tag,
  Timeline,
  Typography,
  message
} from "antd";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { MyLearningReport, getMyLearningReports } from "../api/reports";
import { PageHeader } from "../components/PageHeader";
import { formatCourseStatus } from "../shared/utils/displayText";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

export function LearningReportPage() {
  const navigate = useNavigate();
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

  if (currentUser.role === "mentor") {
    return (
      <>
        <PageHeader title="个人中心" description="查看课程建设、学生参与、资料完善和教学动态。" />
        <Row gutter={[16, 16]}>
          <Col lg={6} md={12} xs={24}>
            <Card className="metric-card teaching-metric">
              <Statistic title="已创建课程" value={report?.created_course_count ?? 0} suffix="门" />
            </Card>
          </Col>
          <Col lg={6} md={12} xs={24}>
            <Card className="metric-card teaching-metric">
              <Statistic title="选课学生" value={report?.student_count ?? 0} suffix="人" />
            </Card>
          </Col>
          <Col lg={6} md={12} xs={24}>
            <Card className="metric-card teaching-metric">
              <Statistic title="课程章节" value={report?.chapter_count ?? 0} suffix="节" />
            </Card>
          </Col>
          <Col lg={6} md={12} xs={24}>
            <Card className="metric-card teaching-metric">
              <Statistic title="课件资料" value={report?.uploaded_file_count ?? 0} suffix="份" />
            </Card>
          </Col>
        </Row>

        <Row className="section-row" gutter={[16, 16]}>
          <Col lg={12} xs={24}>
            <Card className="teaching-panel" title="课程建设进度">
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
            <Card className="teaching-panel" title="教学动态">
              <Timeline items={(report?.recent_activities ?? []).map((activity) => ({ children: activity }))} />
            </Card>
          </Col>
        </Row>

        <Row className="section-row" gutter={[16, 16]}>
          <Col lg={15} xs={24}>
            <Card className="teaching-panel" title="我的课程概览">
              <List
                className="teaching-course-list"
                dataSource={report?.course_summaries ?? []}
                locale={{ emptyText: "暂无课程，先创建一门课程吧" }}
                renderItem={(course) => (
                  <List.Item
                    actions={[
                      <Button key="detail" onClick={() => navigate(`/courses/${course.id}`)} type="link">
                        查看课程
                      </Button>,
                      <Button key="files" onClick={() => navigate("/files")} type="link">
                        上传课件
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      description={
                        <Space wrap>
                          <Tag color={course.status === "published" ? "green" : "default"}>
                            {formatCourseStatus(course.status)}
                          </Tag>
                          <Typography.Text type="secondary">{course.enrollment_count} 名学生</Typography.Text>
                          <Typography.Text type="secondary">{course.chapter_count} 个章节</Typography.Text>
                          <Typography.Text type="secondary">{course.file_count} 份课件</Typography.Text>
                        </Space>
                      }
                      title={course.title}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          <Col lg={9} xs={24}>
            <Card className="teaching-panel" title="教学建议">
              <Space className="teaching-suggestion-list" direction="vertical">
                {(report?.suggestions ?? []).map((suggestion) => (
                  <Typography.Text key={suggestion}>{suggestion}</Typography.Text>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      </>
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
