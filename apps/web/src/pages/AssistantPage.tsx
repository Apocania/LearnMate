import { DownloadOutlined, RobotOutlined, SendOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Avatar, Button, Input, Select, Space, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";

import { AssistantMessageResponse, sendAssistantMessage } from "../api/assistant";
import { getApiBaseUrl } from "../api/client";
import { Course, listCourses } from "../api/courses";
import { PageHeader } from "../components/PageHeader";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

const starterMessages: ChatMessage[] = [
  {
    id: "welcome",
    role: "assistant",
    author: "LearnMate AI",
    content: "你好，我可以结合已上传的课程资料回答问题，也可以帮你整理复习建议。"
  }
];

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  author: string;
  content: string;
  citations?: AssistantMessageResponse["citations"];
};

export function AssistantPage() {
  const currentUser = useCurrentUser();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(starterMessages);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const assistantStatus = useMemo(() => (isSending ? "正在检索..." : "在线"), [isSending]);

  useEffect(() => {
    async function refreshCourses() {
      try {
        setCourses(await listCourses());
      } catch {
        setCourses([]);
      }
    }
    void refreshCourses();
  }, []);

  async function handleSend() {
    const content = input.trim();
    if (!content || !currentUser) {
      return;
    }

    setInput("");
    setChatMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", author: currentUser.username, content }
    ]);
    setIsSending(true);
    try {
      const response = await sendAssistantMessage({ content, course_id: selectedCourseId, session_id: sessionId });
      setSessionId(response.session_id ?? sessionId);
      setChatMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          author: "LearnMate AI",
          content: response.answer,
          citations: response.citations
        }
      ]);
    } catch (error) {
      setChatMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          author: "LearnMate AI",
          content: error instanceof Error ? error.message : "AI伴学暂时无法回答，请稍后再试。"
        }
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function resolveSourceUrl(url?: string | null) {
    if (!url) {
      return undefined;
    }
    return `${getApiBaseUrl()}${url.replace("/api", "")}`;
  }

  return (
    <>
      <PageHeader title="AI伴学" description="结合课程资料检索、引用来源和学习记录，陪你提问、复习和整理知识。" />
      {!currentUser ? (
        <Alert
          className="section-row"
          message="请先登录后使用 AI伴学"
          description="游客可以浏览课程和讨论内容，登录学生或伴学师身份后可以与 AI 交流。"
          showIcon
          type="info"
        />
      ) : null}
      <section className="discord-chat-shell" aria-label="AI 伴学聊天">
        <aside className="chat-sidebar">
          <Typography.Text className="chat-sidebar-label">频道</Typography.Text>
          <button className="chat-channel active" type="button">
            <RobotOutlined />
            <span>课程答疑</span>
          </button>
          <button className="chat-channel" type="button">
            <UserOutlined />
            <span>学习规划</span>
          </button>
          <Select
            allowClear
            className="chat-course-select"
            onChange={(value) => {
              setSelectedCourseId(value ?? null);
              setSessionId(null);
            }}
            options={courses.map((course) => ({ label: course.title, value: course.id }))}
            placeholder="选择课程资料"
            value={selectedCourseId ?? undefined}
          />
        </aside>

        <div className="chat-main">
          <div className="chat-main-header">
            <Space direction="vertical" size={2}>
              <Typography.Title level={4}># 课程答疑</Typography.Title>
              <Typography.Text type="secondary">
                {selectedCourseId ? "优先检索所选课程的课件资料，并在回答下方显示引用。" : "未选择课程时，会在全局资料中检索可用内容。"}
              </Typography.Text>
            </Space>
            <span className={isSending ? "presence typing" : "presence"}>{assistantStatus}</span>
          </div>

          <div className="chat-message-list">
            {chatMessages.map((message) => (
              <article className={message.role === "user" ? "chat-message user" : "chat-message"} key={message.id}>
                <Avatar className="chat-avatar" icon={message.role === "user" ? <UserOutlined /> : <RobotOutlined />} />
                <div className="chat-message-body">
                  <div className="chat-message-meta">
                    <Typography.Text strong>{message.author}</Typography.Text>
                    <Typography.Text type="secondary">刚刚</Typography.Text>
                  </div>
                  <Typography.Paragraph>{message.content}</Typography.Paragraph>
                  {message.citations?.length ? (
                    <Space className="citation-list" direction="vertical" size={8}>
                      {message.citations.map((citation) => (
                        <div className="citation-item" key={`${citation.document_id}-${citation.chunk_index}`}>
                          <Space wrap>
                            <Tag color="blue">{citation.title}</Tag>
                            <Typography.Text type="secondary">第 {citation.chunk_index} 段</Typography.Text>
                            {citation.source_url ? (
                              <Button
                                href={resolveSourceUrl(citation.source_url)}
                                icon={<DownloadOutlined />}
                                size="small"
                                target="_blank"
                              >
                                来源
                              </Button>
                            ) : null}
                          </Space>
                          {citation.snippet ? (
                            <Typography.Paragraph className="citation-snippet">{citation.snippet}</Typography.Paragraph>
                          ) : null}
                        </div>
                      ))}
                    </Space>
                  ) : null}
                </div>
              </article>
            ))}
          </div>

          <div className="chat-composer">
            <Input.TextArea
              disabled={!currentUser || isSending}
              autoSize={{ minRows: 1, maxRows: 5 }}
              onChange={(event) => setInput(event.target.value)}
              onPressEnter={(event) => {
                if (!event.shiftKey) {
                  event.preventDefault();
                  void handleSend();
                }
              }}
              placeholder={currentUser ? "向 #课程答疑 发送消息" : "登录后可以发送消息"}
              value={input}
            />
            <Button
              aria-label="发送消息"
              className="chat-send-button"
              disabled={!currentUser || !input.trim()}
              icon={<SendOutlined />}
              loading={isSending}
              onClick={() => void handleSend()}
              type="primary"
            />
          </div>
        </div>
      </section>
    </>
  );
}
