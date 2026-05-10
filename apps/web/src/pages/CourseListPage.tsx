import { BookOutlined, DeleteOutlined, EditOutlined, PlusOutlined, TeamOutlined } from "@ant-design/icons";
import { Button, Card, Col, Form, Input, Modal, Popconfirm, Row, Space, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useState } from "react";

import { Course, createCourse, deleteCourse, listCourses, updateCourse } from "../api/courses";
import { PageHeader } from "../components/PageHeader";

type CourseFormValues = {
  title: string;
  description: string;
  status: string;
};

export function CourseListPage() {
  const [form] = Form.useForm<CourseFormValues>();
  const [courses, setCourses] = useState<Course[]>([]);
  const [keyword, setKeyword] = useState("");
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function refreshCourses() {
    setIsLoading(true);
    try {
      setCourses(await listCourses());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "课程加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshCourses();
  }, []);

  const filteredCourses = useMemo(() => {
    const normalizedKeyword = keyword.trim().toLowerCase();
    if (!normalizedKeyword) {
      return courses;
    }
    return courses.filter((course) =>
      [course.title, course.description, course.teacher_name].some((value) =>
        value.toLowerCase().includes(normalizedKeyword),
      ),
    );
  }, [courses, keyword]);

  function openCreateModal() {
    setEditingCourse(null);
    form.setFieldsValue({ title: "", description: "", status: "published" });
    setIsModalOpen(true);
  }

  function openEditModal(course: Course) {
    setEditingCourse(course);
    form.setFieldsValue({
      title: course.title,
      description: course.description,
      status: course.status
    });
    setIsModalOpen(true);
  }

  async function handleSubmit(values: CourseFormValues) {
    try {
      if (editingCourse) {
        await updateCourse(editingCourse.id, values);
        message.success("课程已更新");
      } else {
        await createCourse(values);
        message.success("课程已创建");
      }
      setIsModalOpen(false);
      await refreshCourses();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "操作失败");
    }
  }

  async function handleDelete(courseId: number) {
    try {
      await deleteCourse(courseId);
      message.success("课程已删除");
      await refreshCourses();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "删除失败");
    }
  }

  return (
    <>
      <PageHeader title="课程中心" description="浏览课程、查看详情并完成选课。" />
      <Card className="toolbar-card">
        <Space wrap>
          <Input.Search
            allowClear
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="搜索课程、教师或关键词"
            style={{ width: 320 }}
            value={keyword}
          />
          <Button icon={<PlusOutlined />} onClick={openCreateModal} type="primary">
            创建课程
          </Button>
        </Space>
      </Card>
      <Row className="section-row" gutter={[16, 16]}>
        {filteredCourses.map((course) => (
          <Col key={course.id} lg={8} md={12} xs={24}>
            <Card
              actions={[
                <Button icon={<EditOutlined />} key="edit" onClick={() => openEditModal(course)} type="link">
                  编辑
                </Button>,
                <Popconfirm
                  key="delete"
                  okText="删除"
                  onConfirm={() => void handleDelete(course.id)}
                  title="确认删除这门课程？"
                >
                  <Button danger icon={<DeleteOutlined />} type="link">
                    删除
                  </Button>
                </Popconfirm>
              ]}
              className="course-card"
              loading={isLoading}
            >
              <Space direction="vertical" size={12}>
                <BookOutlined className="card-icon" />
                <Typography.Title level={4}>{course.title}</Typography.Title>
                <Typography.Text type="secondary">{course.description}</Typography.Text>
                <Space wrap>
                  <Tag color={course.status === "published" ? "green" : "default"}>{course.status}</Tag>
                </Space>
                <Typography.Text type="secondary">
                  <TeamOutlined /> {course.teacher_name}
                </Typography.Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Modal
        destroyOnHidden
        okText={editingCourse ? "保存修改" : "创建课程"}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        open={isModalOpen}
        title={editingCourse ? "编辑课程" : "创建课程"}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="课程名称" name="title" rules={[{ required: true, message: "请输入课程名称" }]}>
            <Input placeholder="例如：机器学习基础" />
          </Form.Item>
          <Form.Item label="课程说明" name="description" rules={[{ required: true, message: "请输入课程说明" }]}>
            <Input.TextArea autoSize={{ minRows: 4, maxRows: 8 }} placeholder="介绍课程目标、内容和适合人群" />
          </Form.Item>
          <Form.Item label="状态" name="status" rules={[{ required: true }]}>
            <Input placeholder="published / draft" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
