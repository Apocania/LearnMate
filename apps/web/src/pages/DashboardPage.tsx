import {
  BookOutlined,
  CheckCircleOutlined,
  CloudUploadOutlined,
  LineChartOutlined,
  MessageOutlined,
  ReadOutlined,
  RobotOutlined
} from "@ant-design/icons";
import { Button, Card, Col, List, Progress, Row, Space, Statistic, Tag, Typography } from "antd";
import { useNavigate } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";

const learningTasks = [
  "完成《机器学习基础》第 2 章课件阅读",
  "查看 AI 助教整理的梯度下降问答",
  "回复课程论坛中的小组讨论帖"
];

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
    title: "AI伴学",
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

  return (
    <>
      <PageHeader
        eyebrow="智能教学协作空间"
        title="欢迎来到 LearnMate"
        description="以课程为中心，以互动为纽带，以 AI 伴学为辅助，以数据反馈为支撑。"
      />

      <section className="home-command">
        <div className="home-command-copy">
          <Typography.Text className="home-kicker">今日学习工作台</Typography.Text>
          <Typography.Title level={2}>课程、讨论、AI 与成长记录在这里汇合。</Typography.Title>
          <Typography.Paragraph>
            面向学生和伴学师的轻量化学习协作空间，让课程资料、交流答疑和学习反馈保持同一个节奏。
          </Typography.Paragraph>
          <Space wrap>
            <Button icon={<BookOutlined />} onClick={() => navigate("/courses")} type="primary">
              进入课程中心
            </Button>
            <Button icon={<RobotOutlined />} onClick={() => navigate("/assistant")}>
              打开 AI 伴学
            </Button>
          </Space>
        </div>
        <div className="home-command-panel">
          <div className="signal-row">
            <span className="signal-icon">
              <CloudUploadOutlined />
            </span>
            <span>
              <Typography.Text strong>课件资料</Typography.Text>
              <Typography.Text type="secondary">已进入知识库索引</Typography.Text>
            </span>
            <Tag color="green">在线</Tag>
          </div>
          <div className="signal-row">
            <span className="signal-icon">
              <RobotOutlined />
            </span>
            <span>
              <Typography.Text strong>AI 伴学</Typography.Text>
              <Typography.Text type="secondary">可结合课程引用回答</Typography.Text>
            </span>
            <Tag color="blue">就绪</Tag>
          </div>
          <div className="signal-row">
            <span className="signal-icon">
              <CheckCircleOutlined />
            </span>
            <span>
              <Typography.Text strong>学习记录</Typography.Text>
              <Typography.Text type="secondary">自动沉淀关键行为</Typography.Text>
            </span>
            <Tag color="gold">同步</Tag>
          </div>
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
        <Col lg={6} sm={12} xs={24}>
          <Card className="metric-card">
            <Statistic prefix={<BookOutlined />} title="已选课程" value={4} suffix="门" />
          </Card>
        </Col>
        <Col lg={6} sm={12} xs={24}>
          <Card className="metric-card">
            <Statistic prefix={<RobotOutlined />} title="本周 AI 问答" value={18} suffix="次" />
          </Card>
        </Col>
        <Col lg={6} sm={12} xs={24}>
          <Card className="metric-card">
            <Statistic prefix={<MessageOutlined />} title="论坛互动" value={9} suffix="条" />
          </Card>
        </Col>
        <Col lg={6} sm={12} xs={24}>
          <Card className="metric-card">
            <Statistic prefix={<ReadOutlined />} title="学习完成率" value={68} suffix="%" />
          </Card>
        </Col>
      </Row>

      <Row className="section-row" gutter={[16, 16]}>
        <Col lg={15} xs={24}>
          <Card title="最近学习进度">
            <Space className="progress-list" direction="vertical" size="large">
              <div>
                <div className="progress-title">
                  <Typography.Text strong>机器学习基础</Typography.Text>
                  <Tag color="blue">进行中</Tag>
                </div>
                <Progress percent={72} />
              </div>
              <div>
                <div className="progress-title">
                  <Typography.Text strong>教育数据分析</Typography.Text>
                  <Tag color="green">良好</Tag>
                </div>
                <Progress percent={56} />
              </div>
              <div>
                <div className="progress-title">
                  <Typography.Text strong>Python 编程实践</Typography.Text>
                  <Tag color="orange">待复习</Tag>
                </div>
                <Progress percent={41} />
              </div>
            </Space>
          </Card>
        </Col>
        <Col lg={9} xs={24}>
          <Card title="今日建议">
            <List
              dataSource={learningTasks}
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
