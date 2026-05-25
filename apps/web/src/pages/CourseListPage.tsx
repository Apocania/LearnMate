import {
  BookOutlined,
  DeleteOutlined,
  EditOutlined,
  FileAddOutlined,
  PlusOutlined,
  TeamOutlined,
  UserAddOutlined
} from "@ant-design/icons";
import { Button, Card, Col, Form, Input, Modal, Popconfirm, Row, Select, Space, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Course, deleteCourse, enrollCourse, leaveCourse, listCourses, updateCourse } from "../api/courses";
import { PageHeader } from "../components/PageHeader";
import { formatCourseStatus } from "../shared/utils/displayText";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

type CourseFormValues = {
  title: string;
  description: string;
  status: string;
};

export function CourseListPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm<CourseFormValues>();
  const [courses, setCourses] = useState<Course[]>([]);
  const [keyword, setKeyword] = useState("");
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const currentUser = useCurrentUser();
  const isMentor = currentUser?.role === "mentor";
  const isStudent = currentUser?.role === "student";

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
    if (!editingCourse) {
      return;
    }
    try {
      await updateCourse(editingCourse.id, values);
      message.success("课程已更新");
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

  async function handleToggleEnrollment(course: Course) {
    if (!isStudent) {
      message.info("请使用学生身份登录后再选课");
      return;
    }

    try {
      if (course.joined_by_me) {
        await leaveCourse(course.id);
        message.success("已退出课程");
      } else {
        await enrollCourse(course.id);
        message.success("已加入课程");
      }
      await refreshCourses();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "选课操作失败");
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
          {isMentor ? (
            <Button icon={<PlusOutlined />} onClick={() => navigate("/courses/new")} type="primary">
              创建课程
            </Button>
          ) : null}
          {isMentor ? (
            <Button icon={<FileAddOutlined />} onClick={() => navigate("/files")}>
              课件管理
            </Button>
          ) : null}
        </Space>
      </Card>
      <Row className="section-row" gutter={[16, 16]}>
        {filteredCourses.map((course) => (
          <Col key={course.id} lg={8} md={12} xs={24}>
            <Card
              actions={[
                isStudent ? (
                  <Button icon={<UserAddOutlined />} key="enroll" onClick={() => void handleToggleEnrollment(course)} type="link">
                    {course.joined_by_me ? "退出课程" : "加入课程"}
                  </Button>
                ) : null,
                isMentor && currentUser?.id === course.teacher_id ? (
                  <Button icon={<EditOutlined />} key="edit" onClick={() => openEditModal(course)} type="link">
                    编辑
                  </Button>
                ) : null,
                isMentor && currentUser?.id === course.teacher_id ? (
                  <Popconfirm
                    cancelText="取消"
                    key="delete"
                    okText="删除"
                    onConfirm={() => void handleDelete(course.id)}
                    title="确认删除这门课程？"
                  >
                    <Button danger icon={<DeleteOutlined />} type="link">
                      删除
                    </Button>
                  </Popconfirm>
                ) : null
              ].filter(Boolean)}
              className="course-card"
              loading={isLoading}
            >
              <Space direction="vertical" size={12}>
                <BookOutlined className="card-icon" />
                <Typography.Title level={4}>{course.title}</Typography.Title>
                <Typography.Text type="secondary">{course.description}</Typography.Text>
                <Space wrap>
                  {isMentor ? (
                    <Tag color={course.status === "published" ? "green" : "default"}>
                      {formatCourseStatus(course.status)}
                    </Tag>
                  ) : null}
                  {course.joined_by_me ? <Tag color="blue">已加入</Tag> : null}
                  <Tag color="cyan">{course.enrollment_count} 人学习</Tag>
                </Space>
                <Typography.Text type="secondary">
                  <TeamOutlined /> {course.teacher_name}
                </Typography.Text>
                <Button onClick={() => navigate(`/courses/${course.id}`)} type="link">
                  查看详情
                </Button>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Modal
        className="course-edit-modal"
        destroyOnHidden
        cancelText="取消"
        okText="保存修改"
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        open={isModalOpen}
        title="编辑课程"
      >
        <Form className="course-form polished-form" form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item label="课程名称" name="title" rules={[{ required: true, message: "请输入课程名称" }]}>
            <Input placeholder="例如：机器学习基础" />
          </Form.Item>
          <Form.Item label="课程说明" name="description" rules={[{ required: true, message: "请输入课程说明" }]}>
            <Input.TextArea autoSize={{ minRows: 4, maxRows: 8 }} placeholder="介绍课程目标、内容和适合人群" />
          </Form.Item>
          <Form.Item label="状态" name="status" rules={[{ required: true }]}>
            <Select
              options={[
                { label: "已发布", value: "published" },
                { label: "草稿", value: "draft" }
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
