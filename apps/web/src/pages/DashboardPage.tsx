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
  "完成《星际数学探险》的分数任务卡",
  "在《瓶中彩虹》讨论里写下你的观察",
  "向智能伴学提问：为什么 3/4 比 2/3 大？"
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
              <Typography.Text strong>智能伴学</Typography.Text>
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
            <Statistic prefix={<RobotOutlined />} title="本周智能问答" value={18} suffix="次" />
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
                  <Typography.Text strong>星际数学探险</Typography.Text>
                  <Tag color="blue">进行中</Tag>
                </div>
                <Progress percent={72} />
              </div>
              <div>
                <div className="progress-title">
                  <Typography.Text strong>奇妙科学实验室</Typography.Text>
                  <Tag color="green">良好</Tag>
                </div>
                <Progress percent={56} />
              </div>
              <div>
                <div className="progress-title">
                  <Typography.Text strong>编程创意课</Typography.Text>
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
