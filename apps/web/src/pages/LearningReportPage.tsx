import { Card, Col, Progress, Row, Space, Statistic, Timeline, Typography } from "antd";

import { PageHeader } from "../components/PageHeader";

export function LearningReportPage() {
  return (
    <>
      <PageHeader title="个人中心" description="查看学习档案、成长进度和适合你的学习建议。" />
      <Row gutter={[16, 16]}>
        <Col md={8} xs={24}>
          <Card>
            <Statistic title="本周学习时长" value={9.5} suffix="小时" />
          </Card>
        </Col>
        <Col md={8} xs={24}>
          <Card>
            <Statistic title="完成章节" value={12} suffix="节" />
          </Card>
        </Col>
        <Col md={8} xs={24}>
          <Card>
            <Statistic title="AI 辅助问答" value={18} suffix="次" />
          </Card>
        </Col>
      </Row>
      <Row className="section-row" gutter={[16, 16]}>
        <Col lg={12} xs={24}>
          <Card title="能力进度">
            <Space className="progress-list" direction="vertical" size="large">
              <div>
                <Typography.Text>概念理解</Typography.Text>
                <Progress percent={78} />
              </div>
              <div>
                <Typography.Text>实践应用</Typography.Text>
                <Progress percent={62} />
              </div>
              <div>
                <Typography.Text>讨论互动</Typography.Text>
                <Progress percent={54} />
              </div>
            </Space>
          </Card>
        </Col>
        <Col lg={12} xs={24}>
          <Card title="学习轨迹">
            <Timeline
              items={[
                { children: "完成机器学习基础第 2 章" },
                { children: "向 AI 助教提问 3 次" },
                { children: "参与论坛讨论：学习率选择" }
              ]}
            />
          </Card>
        </Col>
      </Row>
    </>
  );
}
