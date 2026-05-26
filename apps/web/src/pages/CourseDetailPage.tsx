import {
  ArrowLeftOutlined,
  BookOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EditOutlined,
  FileAddOutlined,
  PlusOutlined,
  TeamOutlined,
  UserAddOutlined
} from "@ant-design/icons";
import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Input,
  InputNumber,
  List,
  Modal,
  Popconfirm,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
  Upload,
  message
} from "antd";
import type { UploadProps } from "antd";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  Course,
  CourseChapter,
  CourseEnrollment,
  createCourseChapter,
  deleteCourseChapter,
  enrollCourse,
  getCourse,
  leaveCourse,
  listCourseChapters,
  listCourseEnrollments,
  removeCourseEnrollment,
  updateCourseChapter
} from "../api/courses";
import { FileAsset, getFileDownloadUrl, listFiles, uploadFile } from "../api/files";
import { updateCourseProgress } from "../api/learningRecords";
import { PageHeader } from "../components/PageHeader";
import { formatCourseStatus } from "../shared/utils/displayText";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

type ChapterFormValues = {
  title: string;
  description: string;
  sort_order: number;
};

export function CourseDetailPage() {
  const navigate = useNavigate();
  const { courseId } = useParams();
  const currentUser = useCurrentUser();
  const [form] = Form.useForm<ChapterFormValues>();
  const [course, setCourse] = useState<Course | null>(null);
  const [chapters, setChapters] = useState<CourseChapter[]>([]);
  const [enrollments, setEnrollments] = useState<CourseEnrollment[]>([]);
  const [files, setFiles] = useState<FileAsset[]>([]);
  const [editingChapter, setEditingChapter] = useState<CourseChapter | null>(null);
  const [isChapterModalOpen, setIsChapterModalOpen] = useState(false);
  const [uploadingChapterId, setUploadingChapterId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const pendingStudySecondsRef = useRef(0);
  const lastTickRef = useRef(Date.now());
  const maxProgressRef = useRef(0);
  const isStudent = currentUser?.role === "student";
  const isCourseOwner = currentUser?.role === "mentor" && currentUser.id === course?.teacher_id;

  const numericCourseId = useMemo(() => Number(courseId), [courseId]);

  async function refreshCourseBundle() {
    if (!Number.isInteger(numericCourseId) || numericCourseId <= 0) {
      message.error("课程地址无效");
      navigate("/courses");
      return;
    }

    setIsLoading(true);
    try {
      const [nextCourse, nextChapters, nextFiles] = await Promise.all([
        getCourse(numericCourseId),
        listCourseChapters(numericCourseId),
        listFiles({ course_id: numericCourseId })
      ]);
      setCourse(nextCourse);
      setChapters(nextChapters);
      setFiles(nextFiles);
      if (currentUser?.role === "mentor" && currentUser.id === nextCourse.teacher_id) {
        setEnrollments(await listCourseEnrollments(numericCourseId));
      } else {
        setEnrollments([]);
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : "课程加载失败");
      navigate("/courses");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshCourseBundle();
  }, [numericCourseId]);

  const calculateScrollProgress = useCallback(() => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const documentHeight = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
    return Math.min(100, Math.max(0, Math.round(((scrollTop + viewportHeight) / documentHeight) * 100)));
  }, []);

  const flushCourseProgress = useCallback(async () => {
    if (!isStudent || !course?.joined_by_me || !Number.isInteger(numericCourseId)) {
      pendingStudySecondsRef.current = 0;
      return;
    }

    const studySecondsDelta = pendingStudySecondsRef.current;
    const progressPercent = Math.max(maxProgressRef.current, calculateScrollProgress());
    if (studySecondsDelta <= 0 && progressPercent <= 0) {
      return;
    }

    pendingStudySecondsRef.current = 0;
    maxProgressRef.current = progressPercent;
    try {
      await updateCourseProgress({
        course_id: numericCourseId,
        progress_percent: progressPercent,
        study_seconds_delta: studySecondsDelta,
        last_position: `scroll:${progressPercent}`
      });
    } catch {
      pendingStudySecondsRef.current += studySecondsDelta;
    }
  }, [calculateScrollProgress, course?.joined_by_me, isStudent, numericCourseId]);

  useEffect(() => {
    if (!isStudent || !course?.joined_by_me) {
      return;
    }

    lastTickRef.current = Date.now();
    maxProgressRef.current = calculateScrollProgress();
    const handleScroll = () => {
      maxProgressRef.current = Math.max(maxProgressRef.current, calculateScrollProgress());
    };
    const handleBeforeUnload = () => {
      void flushCourseProgress();
    };
    const intervalId = window.setInterval(() => {
      const now = Date.now();
      if (document.visibilityState === "visible") {
        pendingStudySecondsRef.current += Math.min(30, Math.max(0, Math.round((now - lastTickRef.current) / 1000)));
        maxProgressRef.current = Math.max(maxProgressRef.current, calculateScrollProgress());
      }
      lastTickRef.current = now;
      if (pendingStudySecondsRef.current >= 30) {
        void flushCourseProgress();
      }
    }, 10000);

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("beforeunload", handleBeforeUnload);
      void flushCourseProgress();
    };
  }, [calculateScrollProgress, course?.joined_by_me, flushCourseProgress, isStudent]);

  async function refreshChaptersAndFiles() {
    const [nextChapters, nextFiles] = await Promise.all([
      listCourseChapters(numericCourseId),
      listFiles({ course_id: numericCourseId })
    ]);
    setChapters(nextChapters);
    setFiles(nextFiles);
  }

  async function refreshEnrollments() {
    if (!isCourseOwner) {
      setEnrollments([]);
      return;
    }
    setEnrollments(await listCourseEnrollments(numericCourseId));
  }

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

  function openCreateChapterModal() {
    setEditingChapter(null);
    form.setFieldsValue({ title: "", description: "", sort_order: chapters.length + 1 });
    setIsChapterModalOpen(true);
  }

  function openEditChapterModal(chapter: CourseChapter) {
    setEditingChapter(chapter);
    form.setFieldsValue({
      title: chapter.title,
      description: chapter.description,
      sort_order: chapter.sort_order
    });
    setIsChapterModalOpen(true);
  }

  async function handleChapterSubmit(values: ChapterFormValues) {
    if (!course) {
      return;
    }
    try {
      if (editingChapter) {
        await updateCourseChapter(course.id, editingChapter.id, values);
        message.success("章节已更新");
      } else {
        await createCourseChapter(course.id, values);
        message.success("章节已创建");
      }
      setIsChapterModalOpen(false);
      await refreshChaptersAndFiles();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "章节保存失败");
    }
  }

  async function handleDeleteChapter(chapter: CourseChapter) {
    if (!course) {
      return;
    }
    try {
      await deleteCourseChapter(course.id, chapter.id);
      message.success("章节已删除");
      await refreshChaptersAndFiles();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "章节删除失败");
    }
  }

  async function handleRemoveEnrollment(enrollment: CourseEnrollment) {
    if (!course) {
      return;
    }
    try {
      await removeCourseEnrollment(course.id, enrollment.id);
      message.success("学生已移出课程");
      await refreshEnrollments();
      setCourse({ ...course, enrollment_count: Math.max(0, course.enrollment_count - 1) });
    } catch (error) {
      message.error(error instanceof Error ? error.message : "移出学生失败");
    }
  }

  function createUploadRequest(chapterId: number | null): UploadProps["customRequest"] {
    return async (options) => {
      if (!course) {
        return;
      }
      const file = options.file;
      if (!(file instanceof File)) {
        options.onError?.(new Error("请选择有效文件"));
        return;
      }
      setUploadingChapterId(chapterId ?? 0);
      try {
        const uploaded = await uploadFile(file, { course_id: course.id, chapter_id: chapterId });
        options.onSuccess?.(uploaded);
        message.success("课件已上传并加入知识库");
        await refreshChaptersAndFiles();
      } catch (error) {
        options.onError?.(error instanceof Error ? error : new Error("上传失败"));
        message.error(error instanceof Error ? error.message : "上传失败");
      } finally {
        setUploadingChapterId(null);
      }
    };
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
      <PageHeader title={course.title} description="查看课程介绍、章节目录、课件资料和选课信息。" />
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/courses")}>
        返回课程中心
      </Button>

      {!currentUser ? (
        <Alert
          className="section-row"
          message="当前为游客浏览模式"
          description="登录学生身份后可以加入或退出课程，登录伴学师身份后可以维护章节和课件。"
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
                {isCourseOwner ? (
                  <Tag color={course.status === "published" ? "green" : "default"}>
                    {formatCourseStatus(course.status)}
                  </Tag>
                ) : null}
                {course.joined_by_me ? <Tag color="blue">已加入</Tag> : null}
                <Tag color="cyan">{course.enrollment_count} 人学习</Tag>
              </Space>
            </Space>
          </Card>

          <Card
            className="section-row"
            extra={
              isCourseOwner ? (
                <Button icon={<PlusOutlined />} onClick={openCreateChapterModal} type="primary">
                  新建章节
                </Button>
              ) : null
            }
            title="章节与课件"
          >
            <List
              className="chapter-list"
              dataSource={chapters}
              locale={{ emptyText: "暂无章节" }}
              renderItem={(chapter) => {
                const chapterFiles = files.filter((file) => file.chapter_id === chapter.id);
                return (
                  <List.Item className="chapter-item">
                    <Space className="chapter-content" direction="vertical" size={12}>
                      <div className="chapter-heading">
                        <Space wrap>
                          <Tag color="blue">第 {chapter.sort_order} 节</Tag>
                          <Typography.Text strong>{chapter.title}</Typography.Text>
                        </Space>
                        {isCourseOwner ? (
                          <Space>
                            <Button icon={<EditOutlined />} onClick={() => openEditChapterModal(chapter)}>
                              编辑
                            </Button>
                            <Popconfirm
                              cancelText="取消"
                              okText="删除"
                              onConfirm={() => void handleDeleteChapter(chapter)}
                              title="确认删除这个章节？"
                            >
                              <Button danger icon={<DeleteOutlined />}>
                                删除
                              </Button>
                            </Popconfirm>
                          </Space>
                        ) : null}
                      </div>
                      {chapter.description ? (
                        <Typography.Paragraph type="secondary">{chapter.description}</Typography.Paragraph>
                      ) : null}
                      <Space className="chapter-file-row" wrap>
                        {chapterFiles.map((file) => (
                          <Button href={getFileDownloadUrl(file)} icon={<DownloadOutlined />} key={file.id} target="_blank">
                            {file.original_name}
                          </Button>
                        ))}
                        {isCourseOwner ? (
                          <Upload customRequest={createUploadRequest(chapter.id)} maxCount={1} showUploadList={false}>
                            <Button icon={<FileAddOutlined />} loading={uploadingChapterId === chapter.id}>
                              上传到本章节
                            </Button>
                          </Upload>
                        ) : null}
                      </Space>
                    </Space>
                  </List.Item>
                );
              }}
            />
            {isCourseOwner ? (
              <Upload customRequest={createUploadRequest(null)} maxCount={1} showUploadList={false}>
                <Button className="section-row" icon={<FileAddOutlined />} loading={uploadingChapterId === 0}>
                  上传课程通用课件
                </Button>
              </Upload>
            ) : null}
          </Card>
        </Col>
        <Col lg={8} xs={24}>
          <Card title="课程信息">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="伴学师">
                <TeamOutlined /> {course.teacher_name}
              </Descriptions.Item>
              <Descriptions.Item label="学习人数">{course.enrollment_count}</Descriptions.Item>
              <Descriptions.Item label="章节数量">{chapters.length}</Descriptions.Item>
              <Descriptions.Item label="课件数量">{files.length}</Descriptions.Item>
              {isCourseOwner ? (
                <Descriptions.Item label="课程状态">{formatCourseStatus(course.status)}</Descriptions.Item>
              ) : null}
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
          {isCourseOwner ? (
            <Card className="section-row" title="学生名单">
              <List
                dataSource={enrollments}
                locale={{ emptyText: "暂无学生加入" }}
                renderItem={(enrollment) => (
                  <List.Item
                    actions={[
                      <Popconfirm
                        cancelText="取消"
                        key="remove"
                        okText="移出"
                        onConfirm={() => void handleRemoveEnrollment(enrollment)}
                        title="确认将这名学生移出课程？"
                      >
                        <Button danger icon={<DeleteOutlined />} type="link">
                          移出
                        </Button>
                      </Popconfirm>
                    ]}
                  >
                    <List.Item.Meta
                      title={enrollment.student_name}
                      description={`加入时间：${new Date(enrollment.created_at).toLocaleString()}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          ) : null}
        </Col>
      </Row>

      <Modal
        destroyOnHidden
        cancelText="取消"
        okText={editingChapter ? "保存修改" : "创建章节"}
        onCancel={() => setIsChapterModalOpen(false)}
        onOk={() => form.submit()}
        open={isChapterModalOpen}
        title={editingChapter ? "编辑章节" : "新建章节"}
      >
        <Form form={form} layout="vertical" onFinish={handleChapterSubmit}>
          <Form.Item label="章节标题" name="title" rules={[{ required: true, message: "请输入章节标题" }]}>
            <Input placeholder="例如：第 1 章 课程导论" />
          </Form.Item>
          <Form.Item label="章节说明" name="description">
            <Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} placeholder="补充章节目标、内容或学习提示" />
          </Form.Item>
          <Form.Item label="排序" name="sort_order" rules={[{ required: true, message: "请输入排序" }]}>
            <InputNumber min={1} precision={0} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
