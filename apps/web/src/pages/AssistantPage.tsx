import { RobotOutlined, SendOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Avatar, Button, Card, Input, List, Space, Typography } from "antd";
import { useState } from "react";

import { sendAssistantMessage } from "../api/assistant";
import { PageHeader } from "../components/PageHeader";
import { getStoredCurrentUser } from "../shared/utils/currentUser";

const messages = [
  {
    role: "assistant",
    content: "你好，我可以结合课程资料回答问题，也可以帮你整理学习建议。"
  },
  {
    role: "user",
    content: "请解释一下梯度下降为什么要沿着负梯度方向走。"
  },
  {
    role: "assistant",
    content: "负梯度方向是函数值下降最快的局部方向，因此常用于迭代优化模型参数。"
  }
];

type ChatMessage = {
  role: "assistant" | "user";
  content: string;
};

export function AssistantPage() {
  const currentUser = getStoredCurrentUser();
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(messages as ChatMessage[]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  async function handleSend() {
    const content = input.trim();
    if (!content || !currentUser) {
      return;
    }

    setInput("");
    setChatMessages((current) => [...current, { role: "user", content }]);
    setIsSending(true);
    try {
      const response = await sendAssistantMessage({ content });
      setChatMessages((current) => [...current, { role: "assistant", content: response.answer }]);
    } catch (error) {
      setChatMessages((current) => [
        ...current,
        { role: "assistant", content: error instanceof Error ? error.message : "AI伴学暂时无法回答，请稍后再试。" }
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
      <Card className="chat-card">
        <List
          dataSource={chatMessages}
          renderItem={(message) => (
            <List.Item className={message.role === "user" ? "chat-item user" : "chat-item"}>
              <Space align="start">
                <Avatar icon={message.role === "user" ? <UserOutlined /> : <RobotOutlined />} />
                <div className="chat-bubble">
                  <Typography.Text>{message.content}</Typography.Text>
                </div>
              </Space>
            </List.Item>
          )}
        />
        <div className="chat-input-row">
          <Input.TextArea
            disabled={!currentUser || isSending}
            autoSize={{ minRows: 1, maxRows: 4 }}
            onChange={(event) => setInput(event.target.value)}
            onPressEnter={(event) => {
              if (!event.shiftKey) {
                event.preventDefault();
                void handleSend();
              }
            }}
            placeholder="输入课程问题，AI伴学会结合资料回答"
            value={input}
          />
          <Button disabled={!currentUser || !input.trim()} icon={<SendOutlined />} loading={isSending} onClick={() => void handleSend()} type="primary">
            发送
          </Button>
        </div>
      </Card>
    </>
  );
}
