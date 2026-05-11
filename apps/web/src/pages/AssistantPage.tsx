import { RobotOutlined, SendOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Avatar, Button, Input, Space, Typography } from "antd";
import { useMemo, useState } from "react";

import { sendAssistantMessage } from "../api/assistant";
import { PageHeader } from "../components/PageHeader";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

const starterMessages: ChatMessage[] = [
  {
    id: "welcome",
    role: "assistant",
    author: "LearnMate AI",
    content: "你好，我可以结合课程资料回答问题，也可以帮你整理学习建议。"
  },
  {
    id: "sample-user",
    role: "user",
    author: "学生示例",
    content: "请解释一下梯度下降为什么要沿着负梯度方向走。"
  },
  {
    id: "sample-ai",
    role: "assistant",
    author: "LearnMate AI",
    content: "负梯度方向是函数值下降最快的局部方向，因此常用于迭代优化模型参数。"
  }
];

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  author: string;
  content: string;
};

export function AssistantPage() {
  const currentUser = useCurrentUser();
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(starterMessages);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const assistantStatus = useMemo(() => (isSending ? "正在输入..." : "在线"), [isSending]);

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
      const response = await sendAssistantMessage({ content });
      setChatMessages((current) => [
        ...current,
        { id: crypto.randomUUID(), role: "assistant", author: "LearnMate AI", content: response.answer }
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

  return (
    <>
      <PageHeader title="AI伴学" description="像学习伙伴一样陪你提问、复习和整理知识。" />
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
        </aside>

        <div className="chat-main">
          <div className="chat-main-header">
            <Space direction="vertical" size={2}>
              <Typography.Title level={4}># 课程答疑</Typography.Title>
              <Typography.Text type="secondary">当前回答仍来自后端占位 AI，后续会接入真实 RAG 检索。</Typography.Text>
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
