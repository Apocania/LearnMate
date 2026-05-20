import { ArrowLeftOutlined, EyeOutlined, FileMarkdownOutlined, PaperClipOutlined, SendOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Form, Input, Space, Typography, Upload, message } from "antd";
import type { UploadFile, UploadProps } from "antd";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createPost } from "../api/forum";
import { PageHeader } from "../components/PageHeader";
import { renderMarkdown } from "../shared/utils/markdown";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

type PostFormValues = {
  title: string;
  content: string;
};

const defaultMarkdown = `## 我的问题

- 背景：
- 我已经尝试：
- 想请大家帮忙：
`;

export function ForumPostEditorPage() {
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const [form] = Form.useForm<PostFormValues>();
  const [content, setContent] = useState(defaultMarkdown);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const previewHtml = useMemo(() => renderMarkdown(content), [content]);

  const uploadProps: UploadProps = {
    beforeUpload: () => false,
    fileList,
    multiple: true,
    onChange: ({ fileList: nextFileList }) => setFileList(nextFileList.slice(0, 5))
  };

  async function handleSubmit(values: PostFormValues) {
    if (!currentUser) {
      message.info("请登录后再发布帖子");
      return;
    }

    const attachments = fileList.flatMap((item) => (item.originFileObj ? [item.originFileObj] : []));

    setIsSubmitting(true);
    try {
      await createPost({
        title: values.title,
        content: values.content,
        attachments
      });
      message.success("帖子已发布");
      navigate("/forum");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "发帖失败");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <PageHeader title="发布帖子" description="用 Markdown 写清楚问题、想法和附件材料。" />
      {!currentUser ? (
        <Alert className="section-row" message="请先登录后发布帖子" showIcon type="info" />
      ) : null}

      <div className="post-editor-shell">
        <Card className="post-editor-card">
          <div className="post-editor-toolbar">
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/forum")}>
              返回讨论
            </Button>
            <Space>
              <FileMarkdownOutlined />
              <Typography.Text type="secondary">支持标题、列表、加粗、斜体和行内代码</Typography.Text>
            </Space>
          </div>

          <Form
            form={form}
            initialValues={{ content: defaultMarkdown }}
            layout="vertical"
            onFinish={handleSubmit}
          >
            <Form.Item label="标题" name="title" rules={[{ required: true, message: "请输入标题" }]}>
              <Input className="post-title-input" maxLength={80} placeholder="一句话说明你想讨论的问题" />
            </Form.Item>

            <div className="post-editor-grid">
              <Form.Item label="正文 Markdown" name="content" rules={[{ required: true, message: "请输入正文" }]}>
                <Input.TextArea
                  className="markdown-editor"
                  onChange={(event) => setContent(event.target.value)}
                  placeholder="使用 Markdown 写下问题背景、尝试过程和想请大家帮忙的点"
                  value={content}
                />
              </Form.Item>

              <div className="markdown-preview-panel">
                <div className="preview-heading">
                  <EyeOutlined />
                  <Typography.Text strong>实时预览</Typography.Text>
                </div>
                <div
                  className="markdown-preview"
                  dangerouslySetInnerHTML={{ __html: previewHtml || "<p>预览会显示在这里。</p>" }}
                />
              </div>
            </div>

            <Form.Item label="附件">
              <Upload.Dragger {...uploadProps} className="post-attachment-uploader">
                <p className="ant-upload-drag-icon">
                  <PaperClipOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽附件到这里</p>
                <p className="ant-upload-hint">最多 5 个附件，单个大小遵循后端上传限制。</p>
              </Upload.Dragger>
            </Form.Item>

            <div className="post-editor-actions">
              <Button onClick={() => navigate("/forum")}>取消</Button>
              <Button disabled={!currentUser} htmlType="submit" icon={<SendOutlined />} loading={isSubmitting} type="primary">
                发布帖子
              </Button>
            </div>
          </Form>
        </Card>
      </div>
    </>
  );
}
