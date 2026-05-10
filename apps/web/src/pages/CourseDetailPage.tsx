import { Button, Card, Col, Descriptions, List, Row, Space, Tag, Typography } from "antd";

import { PageHeader } from "../components/PageHeader";

export function CourseDetailPage() {
  return (
    <>
      <PageHeader title="课程详情" description="展示课程介绍、章节、资料、论坛和 AI 助教入口。" />
      <Row gutter={[16, 16]}>
        <Col lg={16} xs={24}>
          <Card title="机器学习基础">
            <Typography.Paragraph>
              本课程围绕机器学习核心概念展开，帮助学习者理解模型训练、损失函数、梯度下降和模型评估。
            </Typography.Paragraph>
            <Space wrap>
              <Tag color="blue">AI</Tag>
              <Tag color="green">入门</Tag>
              <Tag color="purple">可选课</Tag>
            </Space>
          </Card>
          <Card className="section-row" title="章节目录">
            <List
              dataSource={["课程导论", "线性回归", "梯度下降", "模型评估"]}
              renderItem={(item, index) => (
                <List.Item actions={[<Button key="learn" type="link">开始学习</Button>]}>
                  第 {index + 1} 章：{item}
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col lg={8} xs={24}>
          <Card title="课程信息">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="授课教师">林老师</Descriptions.Item>
              <Descriptions.Item label="学习人数">86</Descriptions.Item>
              <Descriptions.Item label="课程状态">已发布</Descriptions.Item>
            </Descriptions>
            <Button block className="detail-action" type="primary">
              选择课程
            </Button>
          </Card>
        </Col>
      </Row>
    </>
  );
}
