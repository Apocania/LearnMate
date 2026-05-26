import { DeleteOutlined, DownloadOutlined, PlusOutlined, RobotOutlined, SendOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Avatar, Button, Input, Popconfirm, Select, Space, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  AssistantMessageResponse,
  createAssistantSession,
  getCurrentAssistantSession,
  streamAssistantMessage
} from "../api/assistant";
import { getApiBaseUrl } from "../api/client";
import { Course, listCourses } from "../api/courses";
import { PageHeader } from "../components/PageHeader";
import { UserAvatar } from "../components/UserAvatar";
import { renderMarkdown } from "../shared/utils/markdown";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

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
  const [chatMode, setChatMode] = useState<"qa" | "plan">("qa");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const messageListRef = useRef<HTMLDivElement | null>(null);
  const assistantStatus = useMemo(() => (isSending ? "正在生成..." : "在线"), [isSending]);

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

  useEffect(() => {
    async function refreshHistory() {
      if (!currentUser) {
        setChatMessages([]);
        return;
      }
      try {
        const session = await getCurrentAssistantSession({ course_id: selectedCourseId });
        setSessionId(session.id);
        setChatMessages(
          session.messages.map((item) => ({
            id: String(item.id),
            role: item.role,
            author: item.role === "assistant" ? "LearnMate" : currentUser.username,
            content: item.content,
            citations: item.citations
          }))
        );
      } catch {
        setChatMessages([]);
      }
    }
    void refreshHistory();
  }, [currentUser?.id, selectedCourseId]);

  useEffect(() => {
    const element = messageListRef.current;
    if (element) {
      element.scrollTo({ top: element.scrollHeight, behavior: "smooth" });
    }
  }, [chatMessages]);

  async function handleSend() {
    const content = input.trim();
    if (!content || !currentUser) {
      return;
    }

    setInput("");
    const assistantMessageId = crypto.randomUUID();
    setChatMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", author: currentUser.username, content },
      { id: assistantMessageId, role: "assistant", author: "LearnMate", content: "" }
    ]);
    setIsSending(true);
    try {
      await streamAssistantMessage(
        { content, course_id: selectedCourseId, session_id: sessionId, mode: chatMode },
        {
          onMeta: (event) => {
            setSessionId(event.session_id ?? sessionId);
            setChatMessages((current) =>
              current.map((message) =>
                message.id === assistantMessageId ? { ...message, citations: event.citations } : message
              )
            );
          },
          onDelta: (delta) => {
            setChatMessages((current) =>
              current.map((message) =>
                message.id === assistantMessageId ? { ...message, content: `${message.content}${delta}` } : message
              )
            );
          }
        }
      );
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "智能伴学暂时无法回答，请稍后再试。";
      setChatMessages((current) =>
        current.map((message) =>
          message.id === assistantMessageId
            ? { ...message, content: message.content ? `${message.content}\n\n${errorMessage}` : errorMessage }
            : message
        )
      );
    } finally {
      setIsSending(false);
    }
  }

  async function handleStartNewSession() {
    if (!currentUser) {
      return;
    }
    setIsCreatingSession(true);
    try {
      const session = await createAssistantSession({ course_id: selectedCourseId });
      setSessionId(session.id);
      setChatMessages([]);
      setInput("");
      message.success("已开始新的对话");
    } catch (error) {
      message.error(error instanceof Error ? error.message : "新建对话失败");
    } finally {
      setIsCreatingSession(false);
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
      <PageHeader title="智能伴学" description="结合课程资料检索、引用来源和学习记录，陪你提问、复习和整理知识。" />
      {!currentUser ? (
        <Alert
          className="section-row"
          message="请先登录后使用智能伴学"
          description="游客可以浏览课程和讨论内容，登录学生或伴学师身份后可以与智能伴学交流。"
          showIcon
          type="info"
        />
      ) : null}
      <section className="discord-chat-shell" aria-label="智能伴学聊天">
        <aside className="chat-sidebar">
          <Typography.Text className="chat-sidebar-label">频道</Typography.Text>
          <button
            className={chatMode === "qa" ? "chat-channel active" : "chat-channel"}
            type="button"
            onClick={() => setChatMode("qa")}
          >
            <RobotOutlined />
            <span>课程答疑</span>
          </button>
          <button
            className={chatMode === "plan" ? "chat-channel active" : "chat-channel"}
            type="button"
            onClick={() => setChatMode("plan")}
          >
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
              <Typography.Title level={4}>{chatMode === "qa" ? "课程答疑" : "学习规划"}</Typography.Title>
              <Typography.Text type="secondary">
                {chatMode === "plan"
                  ? "围绕所选课程生成学习路径、今日任务和复习建议。"
                  : selectedCourseId
                    ? "优先检索所选课程的课件资料，并在回答下方显示引用。"
                    : "未选择课程时，会在全局资料中检索可用内容。"}
              </Typography.Text>
            </Space>
            <span className={isSending ? "presence typing" : "presence"}>{assistantStatus}</span>
            <Popconfirm
              cancelText="取消"
              disabled={!currentUser || isSending}
              okText="开始"
              onConfirm={() => void handleStartNewSession()}
              title="清空当前窗口并开始新一轮对话？"
            >
              <Button
                disabled={!currentUser || isSending}
                icon={chatMessages.length ? <DeleteOutlined /> : <PlusOutlined />}
                loading={isCreatingSession}
              >
                新对话
              </Button>
            </Popconfirm>
          </div>

          <div className="chat-message-list" ref={messageListRef}>
            {chatMessages.length === 0 ? (
              <article className="chat-message">
                <Avatar className="chat-avatar" icon={<RobotOutlined />} />
                <div className="chat-message-body">
                  <div className="chat-message-meta">
                    <Typography.Text strong>LearnMate</Typography.Text>
                    <Typography.Text type="secondary">现在</Typography.Text>
                  </div>
                  <div
                    className="chat-markdown markdown-preview"
                    dangerouslySetInnerHTML={{
                      __html: renderMarkdown("你好，我可以结合课程资料回答问题，也可以帮你整理学习规划。选择课程后，回答会更贴近你的学习内容。")
                    }}
                  />
                </div>
              </article>
            ) : null}
            {chatMessages.map((message) => (
              <article className={message.role === "user" ? "chat-message user" : "chat-message"} key={message.id}>
                {message.role === "user" ? (
                  <UserAvatar
                    avatarUrl={currentUser?.username === message.author ? currentUser.avatar_url : null}
                    className="chat-avatar"
                    size={42}
                    username={message.author}
                  />
                ) : (
                  <Avatar className="chat-avatar" icon={<RobotOutlined />} />
                )}
                <div className="chat-message-body">
                  <div className="chat-message-meta">
                    <Typography.Text strong>{message.author}</Typography.Text>
                    <Typography.Text type="secondary">刚刚</Typography.Text>
                  </div>
                  <div
                    className="chat-markdown markdown-preview"
                    dangerouslySetInnerHTML={{
                      __html: renderMarkdown(message.content || (message.role === "assistant" && isSending ? "正在整理回答..." : ""))
                    }}
                  />
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
              placeholder={currentUser ? (chatMode === "qa" ? "向课程答疑发送消息" : "描述你的学习目标或困惑") : "登录后可以发送消息"}
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
