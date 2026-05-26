import {
  BookOutlined,
  CheckCircleOutlined,
  CloudUploadOutlined,
  LineChartOutlined,
  MessageOutlined,
  ReadOutlined,
  RobotOutlined
} from "@ant-design/icons";
import { Button, Card, Col, List, Progress, Row, Skeleton, Space, Statistic, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { MyLearningReport, getMyLearningReports } from "../api/reports";
import { SystemStatusItem, getSystemStatus } from "../api/system";
import { PageHeader } from "../components/PageHeader";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

const moduleCards = [
  {
    icon: <BookOutlined />,
    title: "课程中心",
    description: "课程发布、章节资料和学习参与集中管理。",
    path: "/courses",
    tone: "course"
  },
  {
    icon: <MessageOutlined />,
    title: "讨论交流",
    description: "围绕问题、观点和学习心得形成持续互动。",
    path: "/forum",
    tone: "forum"
  },
  {
    icon: <RobotOutlined />,
    title: "智能伴学",
    description: "结合课程资料检索来源，辅助答疑和复习。",
    path: "/assistant",
    tone: "assistant"
  },
  {
    icon: <LineChartOutlined />,
    title: "个人中心",
    description: "沉淀学习轨迹、进度统计和阶段反馈。",
    path: "/reports/me",
    tone: "report"
  }
];

export function DashboardPage() {
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const [report, setReport] = useState<MyLearningReport | null>(null);
  const [statusItems, setStatusItems] = useState<SystemStatusItem[]>([]);
  const [isLoadingReport, setIsLoadingReport] = useState(false);

  useEffect(() => {
    async function refreshDashboard() {
      try {
        const status = await getSystemStatus();
        setStatusItems(Object.values(status));
      } catch {
        setStatusItems([]);
      }
    }
    void refreshDashboard();
  }, []);

  useEffect(() => {
    async function refreshReport() {
      if (!currentUser) {
        setReport(null);
        return;
      }
      setIsLoadingReport(true);
      try {
        setReport(await getMyLearningReports());
      } catch {
        setReport(null);
      } finally {
        setIsLoadingReport(false);
      }
    }
    void refreshReport();
  }, [currentUser?.id]);

  const metrics = useMemo(() => {
    const interactionCount = (report?.forum_post_count ?? 0) + (report?.forum_comment_count ?? 0);
    const averageProgress = report?.recent_course_progress.length
      ? Math.round(
          report.recent_course_progress.reduce((total, item) => total + item.percent, 0) /
            report.recent_course_progress.length,
        )
      : 0;
    if (currentUser?.role === "mentor") {
      return [
        { title: "创建课程", value: report?.created_course_count ?? 0, suffix: "门", icon: <BookOutlined /> },
        { title: "课程学生", value: report?.student_count ?? 0, suffix: "人", icon: <ReadOutlined /> },
        { title: "论坛互动", value: interactionCount, suffix: "条", icon: <MessageOutlined /> },
        { title: "课程完善度", value: averageProgress, suffix: "%", icon: <LineChartOutlined /> }
      ];
    }
    return [
      { title: "已选课程", value: report?.enrolled_course_count ?? 0, suffix: "门", icon: <BookOutlined /> },
      { title: "智能问答", value: report?.ai_question_count ?? 0, suffix: "次", icon: <RobotOutlined /> },
      { title: "论坛互动", value: interactionCount, suffix: "条", icon: <MessageOutlined /> },
      { title: "学习完成率", value: averageProgress, suffix: "%", icon: <ReadOutlined /> }
    ];
  }, [currentUser?.role, report]);

  const progressItems = report?.recent_course_progress ?? [];
  const tasks = report?.daily_tasks.length
    ? report.daily_tasks
    : currentUser
      ? ["暂无今日建议，完成课程学习或参与讨论后会自动生成。"]
      : ["登录后可查看你的学习建议、最近进度和个人统计。"];

  return (
    <>
      <PageHeader
        eyebrow="小小探索家学习站"
        title="欢迎来到 LearnMate"
        description="课程、讨论、智能答疑和成长记录一起陪伴孩子主动探索。"
      />

      <section className="home-command">
        <div className="home-command-copy">
          <span aria-hidden className="home-decoration home-decoration-sun" />
          <span aria-hidden className="home-decoration home-decoration-cloud" />
          <span aria-hidden className="home-decoration home-decoration-planet" />
          <Typography.Text className="home-kicker">今日学习工作台</Typography.Text>
          <Typography.Title level={2}>今天也一起把知识小星球点亮。</Typography.Title>
          <Typography.Paragraph>
            面向学生和伴学师的轻量化学习协作空间，让每一次阅读、提问、讨论和反馈都变成清楚可见的成长足迹。
          </Typography.Paragraph>
          <Space wrap>
            <Button icon={<BookOutlined />} onClick={() => navigate("/courses")} type="primary">
              进入课程中心
            </Button>
            <Button icon={<RobotOutlined />} onClick={() => navigate("/assistant")}>
              打开智能伴学
            </Button>
          </Space>
        </div>
        <div className="home-command-panel">
          {(statusItems.length ? statusItems : [
            { label: "课件资料", status: "加载中", description: "正在读取状态", tone: "default" as const },
            { label: "智能伴学", status: "加载中", description: "正在读取状态", tone: "default" as const },
            { label: "学习记录", status: "加载中", description: "正在读取状态", tone: "default" as const }
          ]).slice(0, 3).map((item) => (
            <div className="signal-row" key={item.label}>
              <span className="signal-icon">
                {item.label.includes("智能") ? <RobotOutlined /> : item.label.includes("记录") ? <CheckCircleOutlined /> : <CloudUploadOutlined />}
              </span>
              <span>
                <Typography.Text strong>{item.label}</Typography.Text>
                <Typography.Text type="secondary">{item.description}</Typography.Text>
              </span>
              <Tag color={item.tone === "default" ? undefined : item.tone}>{item.status}</Tag>
            </div>
          ))}
        </div>
      </section>

      <Row className="module-grid" gutter={[16, 16]}>
        {moduleCards.map((item) => (
          <Col key={item.title} lg={6} sm={12} xs={24}>
            <button className={`module-card ${item.tone}`} type="button" onClick={() => navigate(item.path)}>
              <span className="module-card-icon">{item.icon}</span>
              <span className="module-card-title">{item.title}</span>
              <span className="module-card-description">{item.description}</span>
            </button>
          </Col>
        ))}
      </Row>

      <Row className="section-row" gutter={[16, 16]}>
        {metrics.map((metric) => (
          <Col key={metric.title} lg={6} sm={12} xs={24}>
            <Card className="metric-card">
              <Statistic prefix={metric.icon} title={metric.title} value={metric.value} suffix={metric.suffix} />
            </Card>
          </Col>
        ))}
      </Row>

      <Row className="section-row" gutter={[16, 16]}>
        <Col lg={15} xs={24}>
          <Card title="最近学习进度">
            {isLoadingReport ? (
              <Skeleton active paragraph={{ rows: 4 }} />
            ) : progressItems.length ? (
              <Space className="progress-list" direction="vertical" size="large">
                {progressItems.map((item) => (
                  <div key={item.id}>
                    <div className="progress-title">
                      <Typography.Text strong>{item.title}</Typography.Text>
                      <Tag color={item.percent >= 80 ? "green" : item.percent >= 45 ? "blue" : "orange"}>{item.status_label}</Tag>
                    </div>
                    <Progress percent={item.percent} />
                  </div>
                ))}
              </Space>
            ) : (
              <Typography.Text type="secondary">暂无最近进度，加入或创建课程后会显示在这里。</Typography.Text>
            )}
          </Card>
        </Col>
        <Col lg={9} xs={24}>
          <Card title="今日建议">
            <List
              dataSource={tasks}
              renderItem={(item) => (
                <List.Item>
                  <Typography.Text>{item}</Typography.Text>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </>
  );
}
