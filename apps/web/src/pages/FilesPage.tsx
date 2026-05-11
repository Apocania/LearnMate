import { DeleteOutlined, DownloadOutlined, InboxOutlined } from "@ant-design/icons";
import { Alert, Button, Card, List, Popconfirm, Space, Typography, Upload, message } from "antd";
import type { UploadProps } from "antd";
import { useEffect, useState } from "react";

import { FileAsset, deleteFile, getFileDownloadUrl, listFiles, uploadFile } from "../api/files";
import { PageHeader } from "../components/PageHeader";
import { getStoredCurrentUser } from "../shared/utils/currentUser";

function formatFileSize(size: number) {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

export function FilesPage() {
  const [files, setFiles] = useState<FileAsset[]>([]);
  const currentUser = getStoredCurrentUser();
  const canUpload = currentUser?.role === "mentor";

  async function refreshFiles() {
    try {
      setFiles(await listFiles());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "文件列表加载失败");
    }
  }

  useEffect(() => {
    void refreshFiles();
  }, []);

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
      const uploaded = await uploadFile(file);
      options.onSuccess?.(uploaded);
      message.success("文件已上传");
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
      <PageHeader title="文件资料" description="上传、浏览和下载课程相关资料。" />
      {canUpload ? (
        <Card>
          <Upload.Dragger customRequest={handleUpload} multiple showUploadList={false}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
            <p className="ant-upload-hint">第一版文件存储在后端本地目录，后续可替换为 MinIO。</p>
          </Upload.Dragger>
        </Card>
      ) : (
        <Alert
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
                  <Space split={<span>·</span>}>
                    <Typography.Text type="secondary">{file.uploader_name}</Typography.Text>
                    <Typography.Text type="secondary">{formatFileSize(file.size)}</Typography.Text>
                    <Typography.Text type="secondary">{file.content_type}</Typography.Text>
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
