import {
  BookOutlined,
  CloudUploadOutlined,
  HeartFilled,
  MessageOutlined,
  NotificationOutlined,
  RobotOutlined,
  UserOutlined
} from "@ant-design/icons";
import { Badge, Button, Layout, Modal, Space, Tooltip, Typography, Upload, message } from "antd";
import type { UploadProps } from "antd";
import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { uploadMyAvatar } from "../api/auth";
import { getUnreadMessageCount } from "../api/messages";
import { clearStoredSession, updateStoredCurrentUser } from "../shared/utils/currentUser";
import { useCurrentUser } from "../shared/utils/useCurrentUser";
import { UserAvatar } from "./UserAvatar";

const navItems = [
  { key: "/courses", icon: <BookOutlined />, label: "课程中心" },
  { key: "/forum", icon: <MessageOutlined />, label: "讨论交流" },
  { key: "/assistant", icon: <RobotOutlined />, label: "智能伴学" },
  { key: "/reports/me", icon: <UserOutlined />, label: "个人中心" }
];

export function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const selectedKey = navItems.find((item) => location.pathname.startsWith(item.key))?.key ?? "";

  useEffect(() => {
    if (!currentUser) {
      setUnreadCount(0);
      return;
    }

    async function refreshUnreadCount() {
      try {
        const result = await getUnreadMessageCount();
        setUnreadCount(result.unread_count);
      } catch {
        setUnreadCount(0);
      }
    }

    void refreshUnreadCount();
    const intervalId = window.setInterval(refreshUnreadCount, 30000);
    return () => window.clearInterval(intervalId);
  }, [currentUser?.id, location.pathname]);

  function handleLogout() {
    clearStoredSession();
    navigate("/login");
  }

  const handleAvatarUpload: UploadProps["customRequest"] = async (options) => {
    const file = options.file;
    if (!(file instanceof File)) {
      options.onError?.(new Error("请选择有效图片"));
      return;
    }

    setIsUploadingAvatar(true);
    try {
      const user = await uploadMyAvatar(file);
      updateStoredCurrentUser(user);
      options.onSuccess?.(user);
      message.success("头像已更新");
    } catch (error) {
      options.onError?.(error instanceof Error ? error : new Error("头像上传失败"));
      message.error(error instanceof Error ? error.message : "头像上传失败");
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  return (
    <Layout className="app-shell">
      <Layout.Header className="top-header">
        <button className="brand-button" type="button" onClick={() => navigate("/")}>
          <span className="brand-mascot">
            <HeartFilled />
          </span>
          <span className="brand-copy">
            <Typography.Text className="brand-title">LearnMate</Typography.Text>
            <Typography.Text className="brand-subtitle">智能学习伙伴</Typography.Text>
          </span>
        </button>

        <nav className="top-nav" aria-label="主导航">
          {navItems.map((item) => (
            <button
              className={selectedKey === item.key ? "top-nav-item active" : "top-nav-item"}
              key={item.key}
              type="button"
              onClick={() => navigate(item.key)}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="header-actions">
          {currentUser ? (
            <>
              <Tooltip title="消息中心">
                <button className="message-icon-button" type="button" onClick={() => navigate("/messages")}>
                  <Badge count={unreadCount} size="small">
                    <NotificationOutlined />
                  </Badge>
                </button>
              </Tooltip>
              <button className="user-avatar-button" type="button" onClick={() => setIsProfileOpen(true)}>
                <UserAvatar avatarUrl={currentUser.avatar_url} size={46} username={currentUser.username} />
                <span className="user-meta">
                  <span className="user-name">{currentUser.username}</span>
                  <span className="user-role">{currentUser.role === "mentor" ? "伴学师" : "学生"}</span>
                </span>
              </button>
              <Button shape="round" onClick={handleLogout}>
                退出
              </Button>
            </>
          ) : (
            <Button shape="round" type="primary" onClick={() => navigate("/login")}>
              登录
            </Button>
          )}
        </div>
      </Layout.Header>

      <Layout.Content className="app-content">
        <div className="content-shell">
          <Outlet />
        </div>
      </Layout.Content>

      <Modal
        destroyOnHidden
        footer={null}
        onCancel={() => setIsProfileOpen(false)}
        open={isProfileOpen}
        title="个人头像"
        width={420}
      >
        {currentUser ? (
          <Space className="profile-modal-content" direction="vertical" size={18}>
            <UserAvatar
              avatarUrl={currentUser.avatar_url}
              className="profile-avatar-preview"
              size={92}
              username={currentUser.username}
            />
            <Space className="profile-modal-copy" direction="vertical" size={2}>
              <Typography.Title level={4}>{currentUser.username}</Typography.Title>
              <Typography.Text type="secondary">
                {currentUser.role === "mentor" ? "伴学师" : "学生"}
              </Typography.Text>
            </Space>
            <Upload.Dragger
              accept="image/png,image/jpeg,image/webp,image/gif"
              customRequest={handleAvatarUpload}
              maxCount={1}
              showUploadList={false}
            >
              <p className="ant-upload-drag-icon">
                <CloudUploadOutlined />
              </p>
              <p className="ant-upload-text">{isUploadingAvatar ? "正在上传头像..." : "点击或拖拽图片上传头像"}</p>
              <p className="ant-upload-hint">支持常见图片格式，单张不超过 3 兆。</p>
            </Upload.Dragger>
          </Space>
        ) : null}
      </Modal>
    </Layout>
  );
}
