import { DeleteOutlined, DownloadOutlined, InboxOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, List, Popconfirm, Row, Select, Space, Tag, Typography, Upload, message } from "antd";
import type { UploadProps } from "antd";
import { useEffect, useMemo, useState } from "react";

import { Course, CourseChapter, listCourseChapters, listCourses } from "../api/courses";
import { FileAsset, deleteFile, getFileDownloadUrl, listFiles, uploadFile } from "../api/files";
import { PageHeader } from "../components/PageHeader";
import { formatContentType, formatStorageProvider } from "../shared/utils/displayText";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

function formatFileSize(size: number) {
  if (size < 1024) {
    return `${size} 字节`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} 千字节`;
  }
  return `${(size / 1024 / 1024).toFixed(1)} 兆字节`;
}

export function FilesPage() {
  const [files, setFiles] = useState<FileAsset[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [chapters, setChapters] = useState<CourseChapter[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [selectedChapterId, setSelectedChapterId] = useState<number | null>(null);
  const currentUser = useCurrentUser();
  const canUpload = currentUser?.role === "mentor";

  const courseTitleById = useMemo(() => new Map(courses.map((course) => [course.id, course.title])), [courses]);
  const chapterTitleById = useMemo(() => new Map(chapters.map((chapter) => [chapter.id, chapter.title])), [chapters]);

  async function refreshFiles() {
    try {
      setFiles(await listFiles({ course_id: selectedCourseId }));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "文件列表加载失败");
    }
  }

  async function refreshCourses() {
    try {
      setCourses(await listCourses());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "课程加载失败");
    }
  }

  async function refreshChapters(courseId: number | null) {
    if (!courseId) {
      setChapters([]);
      setSelectedChapterId(null);
      return;
    }
    try {
      setChapters(await listCourseChapters(courseId));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "章节加载失败");
    }
  }

  useEffect(() => {
    void refreshCourses();
  }, []);

  useEffect(() => {
    void refreshFiles();
    void refreshChapters(selectedCourseId);
  }, [selectedCourseId]);

  const handleUpload: UploadProps["customRequest"] = async (options) => {
    const file = options.file;
    if (!canUpload) {
      options.onError?.(new Error("只有伴学师可以上传课件"));
      message.info("只有伴学师可以上传课件");
      return;
    }

    if (!(file instanceof File)) {
      options.onError?.(new Error("请选择有效文件"));
      return;
    }

    try {
      const uploaded = await uploadFile(file, { course_id: selectedCourseId, chapter_id: selectedChapterId });
      options.onSuccess?.(uploaded);
      message.success("文件已上传并加入智能知识库");
      await refreshFiles();
    } catch (error) {
      options.onError?.(error instanceof Error ? error : new Error("上传失败"));
      message.error(error instanceof Error ? error.message : "上传失败");
    }
  };

  async function handleDelete(file: FileAsset) {
    try {
      await deleteFile(file.id);
      message.success("课件已删除");
      await refreshFiles();
    } catch (error) {
      message.error(error instanceof Error ? error.message : "删除失败");
    }
  }

  return (
    <>
      <PageHeader title="文件资料" description="上传、浏览和下载课程相关资料，上传后会自动进入智能伴学知识库。" />
      <Card>
        <Row gutter={[12, 12]}>
          <Col md={10} xs={24}>
            <Select
              allowClear
              className="full-width-control"
              onChange={(value) => {
                setSelectedCourseId(value ?? null);
                setSelectedChapterId(null);
              }}
              options={courses.map((course) => ({ label: course.title, value: course.id }))}
              placeholder="筛选或绑定课程"
              value={selectedCourseId ?? undefined}
            />
          </Col>
          <Col md={10} xs={24}>
            <Select
              allowClear
              className="full-width-control"
              disabled={!selectedCourseId}
              onChange={(value) => setSelectedChapterId(value ?? null)}
              options={chapters.map((chapter) => ({ label: chapter.title, value: chapter.id }))}
              placeholder="绑定章节，可选"
              value={selectedChapterId ?? undefined}
            />
          </Col>
          <Col md={4} xs={24}>
            <Button block onClick={() => void refreshFiles()}>
              刷新
            </Button>
          </Col>
        </Row>
      </Card>

      {canUpload ? (
        <Card className="section-row">
          <Upload.Dragger customRequest={handleUpload} multiple showUploadList={false}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
            <p className="ant-upload-hint">支持文档、图片和文本资料；文本类资料会自动切片供智能伴学检索。</p>
          </Upload.Dragger>
        </Card>
      ) : (
        <Alert
          className="section-row"
          message="当前只能浏览和下载课件"
          description="上传课件需要使用伴学师身份登录。"
          showIcon
          type="info"
        />
      )}

      <Card className="section-row" title="已上传文件">
        <List
          dataSource={files}
          locale={{ emptyText: "暂无文件" }}
          renderItem={(file) => (
            <List.Item
              actions={[
                <Button href={getFileDownloadUrl(file)} icon={<DownloadOutlined />} key="download" target="_blank">
                  浏览/下载
                </Button>,
                canUpload && currentUser?.id === file.uploader_id ? (
                  <Popconfirm
                    cancelText="取消"
                    key="delete"
                    okText="删除"
                    onConfirm={() => void handleDelete(file)}
                    title="确认删除这个课件？"
                  >
                    <Button danger icon={<DeleteOutlined />}>
                      删除
                    </Button>
                  </Popconfirm>
                ) : null
              ].filter(Boolean)}
            >
              <List.Item.Meta
                description={
                  <Space wrap split={<span>·</span>}>
                    <Typography.Text type="secondary">{file.uploader_name}</Typography.Text>
                    <Typography.Text type="secondary">{formatFileSize(file.size)}</Typography.Text>
                    <Typography.Text type="secondary">{formatContentType(file.content_type)}</Typography.Text>
                    <Tag>{formatStorageProvider(file.storage_provider)}</Tag>
                    {file.course_id ? <Tag color="blue">{courseTitleById.get(file.course_id) ?? `课程 #${file.course_id}`}</Tag> : null}
                    {file.chapter_id ? <Tag color="cyan">{chapterTitleById.get(file.chapter_id) ?? `章节 #${file.chapter_id}`}</Tag> : null}
                  </Space>
                }
                title={file.original_name}
              />
            </List.Item>
          )}
        />
      </Card>
    </>
  );
}
