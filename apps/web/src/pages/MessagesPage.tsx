import { BellOutlined, CheckCircleOutlined, MailOutlined, NotificationOutlined, SendOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, Form, Input, List, Row, Select, Space, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Course, listCourses } from "../api/courses";
import {
  StudentRecipient,
  UserMessage,
  listMessages,
  listStudentRecipients,
  markAllMessagesAsRead,
  markMessageAsRead,
  sendAnnouncement,
  sendPrivateMessage
} from "../api/messages";
import { PageHeader } from "../components/PageHeader";
import { formatDate } from "../shared/utils/formatDate";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

type PrivateMessageFormValues = {
  course_id: number;
  recipient_username: string;
  title: string;
  content: string;
};

type AnnouncementFormValues = {
  course_id: number;
  title: string;
  content: string;
};

const messageTypeLabels: Record<UserMessage["message_type"], string> = {
  like: "点赞",
  comment: "评论",
  private: "私信",
  announcement: "公告"
};

const messageTypeColors: Record<UserMessage["message_type"], string> = {
  like: "blue",
  comment: "cyan",
  private: "purple",
  announcement: "gold"
};

export function MessagesPage() {
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const [privateForm] = Form.useForm<PrivateMessageFormValues>();
  const [announcementForm] = Form.useForm<AnnouncementFormValues>();
  const [messages, setMessages] = useState<UserMessage[]>([]);
  const [students, setStudents] = useState<StudentRecipient[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const isMentor = currentUser?.role === "mentor";
  const selectedPrivateCourseId = Form.useWatch("course_id", privateForm);
  const selectedAnnouncementCourseId = Form.useWatch("course_id", announcementForm);

  const unreadCount = useMemo(() => messages.filter((item) => !item.is_read).length, [messages]);
  const ownedCourses = useMemo(() => courses.filter((course) => course.teacher_id === currentUser?.id), [courses, currentUser?.id]);
  const privateStudents = useMemo(() => students.filter((student) => student.course_id === selectedPrivateCourseId), [students, selectedPrivateCourseId]);
  const announcementStudentCount = useMemo(
    () => students.filter((student) => student.course_id === selectedAnnouncementCourseId).length,
    [students, selectedAnnouncementCourseId],
  );

  async function refreshMessages() {
    if (!currentUser) {
      return;
    }
    setIsLoading(true);
    try {
      setMessages(await listMessages());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "消息加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function refreshStudents() {
    if (!isMentor) {
      return;
    }
    try {
      const [studentRows, courseRows] = await Promise.all([listStudentRecipients(), listCourses()]);
      setStudents(studentRows);
      setCourses(courseRows);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "课程学生列表加载失败");
    }
  }

  useEffect(() => {
    void refreshMessages();
  }, [currentUser?.id]);

  useEffect(() => {
    void refreshStudents();
  }, [currentUser?.id, currentUser?.role]);

  async function handleRead(messageItem: UserMessage) {
    if (messageItem.is_read) {
      return;
    }
    try {
      const updatedMessage = await markMessageAsRead(messageItem.id);
      setMessages((previous) =>
        previous.map((item) => (item.id === updatedMessage.id ? updatedMessage : item)),
      );
    } catch (error) {
      message.error(error instanceof Error ? error.message : "标记已读失败");
    }
  }

  async function handleReadAll() {
    try {
      await markAllMessagesAsRead();
      setMessages((previous) => previous.map((item) => ({ ...item, is_read: true })));
      message.success("已全部标记为已读");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "操作失败");
    }
  }

  async function handleSendPrivate(values: PrivateMessageFormValues) {
    setIsSending(true);
    try {
      await sendPrivateMessage(values);
      privateForm.resetFields();
      message.success("私信已发送");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "私信发送失败");
    } finally {
      setIsSending(false);
    }
  }

  async function handleSendAnnouncement(values: AnnouncementFormValues) {
    setIsSending(true);
    try {
      const result = await sendAnnouncement(values);
      announcementForm.resetFields();
      message.success(`公告已发送给 ${result.created_count} 名学生`);
    } catch (error) {
      message.error(error instanceof Error ? error.message : "公告发送失败");
    } finally {
      setIsSending(false);
    }
  }

  function handleSourceClick(messageItem: UserMessage) {
    if (messageItem.source_type === "forum_post") {
      navigate("/forum");
    }
  }

  if (!currentUser) {
    return (
      <>
        <PageHeader title="消息中心" description="查看互动提醒、私信和公告。" />
        <Alert message="请先登录后查看消息" showIcon type="info" />
      </>
    );
  }

  return (
    <>
      <PageHeader title="消息中心" description="查看点赞、评论、私信和公告提醒。" />

      <Row gutter={[16, 16]}>
        <Col lg={isMentor ? 14 : 24} xs={24}>
          <Card
            extra={
              <Space>
                <Tag color={unreadCount > 0 ? "red" : "default"}>{unreadCount} 未读</Tag>
                <Button disabled={unreadCount === 0} icon={<CheckCircleOutlined />} onClick={() => void handleReadAll()}>
                  全部已读
                </Button>
              </Space>
            }
            title="我的消息"
          >
            <List
              className="message-list"
              dataSource={messages}
              loading={isLoading}
              locale={{ emptyText: "暂无消息" }}
              renderItem={(messageItem) => (
                <List.Item
                  className={messageItem.is_read ? "message-item" : "message-item unread"}
                  actions={[
                    messageItem.source_type === "forum_post" ? (
                      <Button key="source" onClick={() => handleSourceClick(messageItem)} type="link">
                        查看来源
                      </Button>
                    ) : null,
                    !messageItem.is_read ? (
                      <Button key="read" onClick={() => void handleRead(messageItem)} type="link">
                        标为已读
                      </Button>
                    ) : null
                  ].filter(Boolean)}
                >
                  <List.Item.Meta
                    avatar={
                      <span className={`message-kind ${messageItem.message_type}`}>
                        {messageItem.message_type === "announcement" ? <NotificationOutlined /> : <BellOutlined />}
                      </span>
                    }
                    description={
                      <Space direction="vertical" size={6}>
                        <Space wrap split={<span>·</span>}>
                          <Tag color={messageTypeColors[messageItem.message_type]}>
                            {messageTypeLabels[messageItem.message_type]}
                          </Tag>
                          {messageItem.sender_name ? (
                            <Typography.Text type="secondary">来自 {messageItem.sender_name}</Typography.Text>
                          ) : null}
                          <Typography.Text type="secondary">{formatDate(messageItem.created_at)}</Typography.Text>
                        </Space>
                        <Typography.Paragraph className="message-content">{messageItem.content}</Typography.Paragraph>
                      </Space>
                    }
                    title={
                      <Typography.Text strong>
                        {!messageItem.is_read ? <span className="unread-dot" /> : null}
                        {messageItem.title}
                      </Typography.Text>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {isMentor ? (
          <Col lg={10} xs={24}>
            <Space className="message-compose-stack" direction="vertical" size={16}>
              <Card title="发送私信">
                <Form form={privateForm} layout="vertical" onFinish={handleSendPrivate}>
                  <Form.Item label="所属课程" name="course_id" rules={[{ required: true, message: "请选择课程" }]}>
                    <Select
                      onChange={() => privateForm.setFieldValue("recipient_username", undefined)}
                      options={ownedCourses.map((course) => ({
                        label: course.title,
                        value: course.id
                      }))}
                      placeholder="选择要沟通的课程"
                    />
                  </Form.Item>
                  <Form.Item label="收件学生" name="recipient_username" rules={[{ required: true, message: "请选择学生" }]}>
                    <Select
                      disabled={!selectedPrivateCourseId}
                      showSearch
                      optionFilterProp="label"
                      options={privateStudents.map((student) => ({
                        label: student.username,
                        value: student.username
                      }))}
                      placeholder={selectedPrivateCourseId ? "选择本课程学生" : "先选择课程"}
                    />
                  </Form.Item>
                  <Form.Item label="标题" name="title" rules={[{ required: true, message: "请输入标题" }]}>
                    <Input maxLength={80} placeholder="例如：作业反馈" />
                  </Form.Item>
                  <Form.Item label="内容" name="content" rules={[{ required: true, message: "请输入内容" }]}>
                    <Input.TextArea autoSize={{ minRows: 4, maxRows: 8 }} maxLength={1000} placeholder="写下私信内容" />
                  </Form.Item>
                  <Button htmlType="submit" icon={<MailOutlined />} loading={isSending} type="primary">
                    发送私信
                  </Button>
                </Form>
              </Card>

              <Card title="发布公告">
                <Form form={announcementForm} layout="vertical" onFinish={handleSendAnnouncement}>
                  <Form.Item label="接收课程" name="course_id" rules={[{ required: true, message: "请选择课程" }]}>
                    <Select
                      options={ownedCourses.map((course) => ({
                        label: course.title,
                        value: course.id
                      }))}
                      placeholder="选择公告接收课程"
                    />
                  </Form.Item>
                  {selectedAnnouncementCourseId ? (
                    <Alert
                      className="form-inline-alert"
                      message={`将发送给该课程 ${announcementStudentCount} 名学生`}
                      showIcon
                      type={announcementStudentCount > 0 ? "info" : "warning"}
                    />
                  ) : null}
                  <Form.Item label="公告标题" name="title" rules={[{ required: true, message: "请输入公告标题" }]}>
                    <Input maxLength={80} placeholder="例如：本周学习安排" />
                  </Form.Item>
                  <Form.Item label="公告内容" name="content" rules={[{ required: true, message: "请输入公告内容" }]}>
                    <Input.TextArea autoSize={{ minRows: 4, maxRows: 8 }} maxLength={1200} placeholder="面向所选课程学生发布公告" />
                  </Form.Item>
                  <Button htmlType="submit" icon={<SendOutlined />} loading={isSending} type="primary">
                    发布公告
                  </Button>
                </Form>
              </Card>
            </Space>
          </Col>
        ) : null}
      </Row>
    </>
  );
}
