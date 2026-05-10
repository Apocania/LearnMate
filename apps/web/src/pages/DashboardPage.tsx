import { BookOutlined, MessageOutlined, ReadOutlined, RobotOutlined } from "@ant-design/icons";
import { Card, Col, List, Progress, Row, Space, Statistic, Tag, Typography } from "antd";

import { PageHeader } from "../components/PageHeader";

const learningTasks = [
  "完成《机器学习基础》第 2 章课件阅读",
  "查看 AI 助教整理的梯度下降问答",
  "回复课程论坛中的小组讨论帖"
];

export function DashboardPage() {
  return (
    <>
      <PageHeader title="欢迎来到 LearnMate" description="从课程、讨论、AI伴学和成长记录开始今天的学习。" />
      <Row gutter={[16, 16]}>
        <Col lg={6} sm={12} xs={24}>
          <Card>
            <Statistic prefix={<BookOutlined />} title="已选课程" value={4} suffix="门" />
          </Card>
        </Col>
        <Col lg={6} sm={12} xs={24}>
          <Card>
            <Statistic prefix={<RobotOutlined />} title="本周 AI 问答" value={18} suffix="次" />
          </Card>
        </Col>
        <Col lg={6} sm={12} xs={24}>
          <Card>
            <Statistic prefix={<MessageOutlined />} title="论坛互动" value={9} suffix="条" />
          </Card>
        </Col>
        <Col lg={6} sm={12} xs={24}>
          <Card>
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
