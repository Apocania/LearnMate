import { ArrowLeftOutlined, BookOutlined, TeamOutlined, UserAddOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, Descriptions, Row, Space, Spin, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Course, enrollCourse, getCourse, leaveCourse } from "../api/courses";
import { PageHeader } from "../components/PageHeader";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

export function CourseDetailPage() {
  const navigate = useNavigate();
  const { courseId } = useParams();
  const currentUser = useCurrentUser();
  const [course, setCourse] = useState<Course | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const isStudent = currentUser?.role === "student";

  async function refreshCourse() {
    const numericCourseId = Number(courseId);
    if (!Number.isInteger(numericCourseId) || numericCourseId <= 0) {
      message.error("课程地址无效");
      navigate("/courses");
      return;
    }

    setIsLoading(true);
    try {
      setCourse(await getCourse(numericCourseId));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "课程加载失败");
      navigate("/courses");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshCourse();
  }, [courseId]);

  async function handleToggleEnrollment() {
    if (!course || !isStudent) {
      message.info("请使用学生身份登录后再选课");
      return;
    }

    setIsSaving(true);
    try {
      const nextCourse = course.joined_by_me ? await leaveCourse(course.id) : await enrollCourse(course.id);
      setCourse(nextCourse);
      message.success(nextCourse.joined_by_me ? "已加入课程" : "已退出课程");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "选课操作失败");
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <div className="page-loading">
        <Spin /> 加载课程中...
      </div>
    );
  }

  if (!course) {
    return null;
  }

  return (
    <>
      <PageHeader title={course.title} description="查看课程介绍、状态、伴学师和选课信息。" />
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/courses")}>
        返回课程中心
      </Button>

      {!currentUser ? (
        <Alert
          className="section-row"
          message="当前为游客浏览模式"
          description="登录学生身份后可以加入或退出课程。"
          showIcon
          type="info"
        />
      ) : null}

      <Row className="section-row" gutter={[16, 16]}>
        <Col lg={16} xs={24}>
          <Card title="课程介绍">
            <Space direction="vertical" size={16}>
              <BookOutlined className="card-icon" />
              <Typography.Paragraph>{course.description}</Typography.Paragraph>
              <Space wrap>
                <Tag color={course.status === "published" ? "green" : "default"}>
                  {course.status === "published" ? "已发布" : "草稿"}
                </Tag>
                {course.joined_by_me ? <Tag color="blue">已加入</Tag> : null}
                <Tag color="cyan">{course.enrollment_count} 人学习</Tag>
              </Space>
            </Space>
          </Card>
          <Card className="section-row" title="后续规划">
            <Typography.Paragraph type="secondary">
              章节目录、课程课件绑定和课程内讨论筛选尚未接入；当前详情页展示真实课程基础信息和选课状态。
            </Typography.Paragraph>
          </Card>
        </Col>
        <Col lg={8} xs={24}>
          <Card title="课程信息">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="伴学师">
                <TeamOutlined /> {course.teacher_name}
              </Descriptions.Item>
              <Descriptions.Item label="学习人数">{course.enrollment_count}</Descriptions.Item>
              <Descriptions.Item label="课程状态">{course.status === "published" ? "已发布" : "草稿"}</Descriptions.Item>
            </Descriptions>
            {isStudent ? (
              <Button
                block
                className="detail-action"
                icon={<UserAddOutlined />}
                loading={isSaving}
                onClick={() => void handleToggleEnrollment()}
                type={course.joined_by_me ? "default" : "primary"}
              >
                {course.joined_by_me ? "退出课程" : "加入课程"}
              </Button>
            ) : null}
          </Card>
        </Col>
      </Row>
    </>
  );
}
