import { ArrowLeftOutlined, BookOutlined, CheckCircleOutlined, FileTextOutlined, RocketOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, Select, Space, Typography, message } from "antd";
import { useNavigate } from "react-router-dom";

import { createCourse } from "../api/courses";
import { PageHeader } from "../components/PageHeader";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

type CourseCreateFormValues = {
  title: string;
  description: string;
  status: string;
};

export function CourseCreatePage() {
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const [form] = Form.useForm<CourseCreateFormValues>();
  const isMentor = currentUser?.role === "mentor";

  async function handleSubmit(values: CourseCreateFormValues) {
    if (!isMentor) {
      message.info("只有伴学师可以创建课程");
      return;
    }

    try {
      const course = await createCourse(values);
      message.success("课程已创建");
      navigate(`/courses/${course.id}`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "课程创建失败");
    }
  }

  return (
    <>
      <PageHeader title="创建课程" description="填写课程介绍、发布状态和学习目标，为学生准备一门清晰好懂的新课程。" />

      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/courses")}>
        返回课程中心
      </Button>

      <Card className="course-create-card interactive-card">
        <div className="course-create-layout">
          <section className="course-create-main">
            <div className="course-create-heading">
              <span className="course-create-icon">
                <BookOutlined />
              </span>
              <Space direction="vertical" size={2}>
                <Typography.Title level={3}>课程基本信息</Typography.Title>
                <Typography.Text type="secondary">标题要直观，说明要告诉学生会学到什么、适合谁。</Typography.Text>
              </Space>
            </div>

            <Form
              className="course-form polished-form"
              form={form}
              initialValues={{ title: "", description: "", status: "published" }}
              layout="vertical"
              onFinish={handleSubmit}
            >
              <Form.Item label="课程名称" name="title" rules={[{ required: true, message: "请输入课程名称" }]}>
                <Input maxLength={80} placeholder="例如：星际数学探险" size="large" />
              </Form.Item>

              <Form.Item label="课程说明" name="description" rules={[{ required: true, message: "请输入课程说明" }]}>
                <Input.TextArea
                  autoSize={{ minRows: 7, maxRows: 12 }}
                  maxLength={1600}
                  placeholder="写清课程目标、主要内容、适合学生和学习方式。"
                />
              </Form.Item>

              <Form.Item label="课程状态" name="status" rules={[{ required: true }]}>
                <Select
                  size="large"
                  options={[
                    { label: "立即发布", value: "published" },
                    { label: "保存草稿", value: "draft" }
                  ]}
                />
              </Form.Item>

              <div className="course-create-actions">
                <Button onClick={() => navigate("/courses")}>取消</Button>
                <Button disabled={!isMentor} htmlType="submit" icon={<RocketOutlined />} type="primary">
                  创建课程
                </Button>
              </div>
            </Form>
          </section>

          <aside className="course-create-side">
            <div className="course-create-panel">
              <FileTextOutlined className="course-create-side-icon" />
              <Typography.Title level={4}>创建后可以继续完善</Typography.Title>
              <Typography.Text type="secondary">进入课程详情后，可添加章节、上传课件，并查看学生名单。</Typography.Text>
            </div>
            <div className="course-create-panel">
              <Typography.Text strong>发布说明</Typography.Text>
              <Space align="start">
                <CheckCircleOutlined className="course-create-check" />
                <Typography.Text type="secondary">发布课程会对学生可见，学生可以加入学习。</Typography.Text>
              </Space>
              <Space align="start">
                <CheckCircleOutlined className="course-create-check" />
                <Typography.Text type="secondary">草稿课程仅创建它的伴学师可见。</Typography.Text>
              </Space>
            </div>
          </aside>
        </div>
      </Card>
    </>
  );
}
