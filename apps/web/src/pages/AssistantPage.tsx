import { RobotOutlined, SendOutlined, UserOutlined } from "@ant-design/icons";
import { Avatar, Button, Card, Input, List, Space, Typography } from "antd";

import { PageHeader } from "../components/PageHeader";

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

export function AssistantPage() {
  return (
    <>
      <PageHeader title="AI伴学" description="像学习伙伴一样陪你提问、复习和整理知识。" />
      <Card className="chat-card">
        <List
          dataSource={messages}
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
          <Input.TextArea autoSize={{ minRows: 1, maxRows: 4 }} placeholder="输入课程问题，AI伴学会结合资料回答" />
          <Button icon={<SendOutlined />} type="primary">
            发送
          </Button>
        </div>
      </Card>
    </>
  );
}
