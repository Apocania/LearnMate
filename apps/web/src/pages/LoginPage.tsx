import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Alert, Button, Card, Form, Input, Radio, Segmented, Space, Typography } from "antd";

import { login, register } from "../api/auth";
import type { UserRole } from "../shared/types/user";

const roleOptions: Array<{ label: string; value: UserRole }> = [
  { label: "学生", value: "student" },
  { label: "伴学师", value: "mentor" }
];

export function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (mode === "register" && password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }

    setIsSubmitting(true);

    try {
      const response =
        mode === "login"
          ? await login({ username, password })
          : await register({ username, password, role });

      localStorage.setItem("learnmate_access_token", response.access_token);
      localStorage.setItem("learnmate_current_user", JSON.stringify(response.user));
      navigate("/");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "操作失败，请稍后重试");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <Card className="auth-card">
        <Space className="auth-heading" direction="vertical" size={6}>
          <div className="auth-logo">L</div>
          <Typography.Title level={2}>LearnMate</Typography.Title>
          <Typography.Text type="secondary">登录或注册后进入智能学习伙伴平台</Typography.Text>
        </Space>

        <Segmented
          block
          className="auth-segmented"
          value={mode}
          options={[
            { label: "登录", value: "login" },
            { label: "注册", value: "register" }
          ]}
          onChange={(value) => {
            setMode(value as "login" | "register");
            setError("");
            setConfirmPassword("");
          }}
        />

        <Form layout="vertical" onSubmitCapture={handleSubmit}>
          <Form.Item label="用户名" required>
            <Input
              minLength={3}
              maxLength={32}
              required
              size="large"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="3-32 位英文、数字或下划线"
            />
            <Typography.Text type="secondary">用户名会统一保存为小写，支持英文、数字和下划线。</Typography.Text>
          </Form.Item>

          <Form.Item label="密码" required>
            <Input.Password
              minLength={6}
              maxLength={128}
              required
              size="large"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="至少 6 位"
            />
          </Form.Item>

          {mode === "register" ? (
            <>
              <Form.Item label="确认密码" required>
                <Input.Password
                  minLength={6}
                  maxLength={128}
                  required
                  size="large"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="请再次输入密码"
                />
              </Form.Item>

              <Form.Item label="选择身份" required>
                <Radio.Group
                  className="role-radio-group"
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                >
                  {roleOptions.map((option) => (
                    <Radio.Button key={option.value} value={option.value}>
                      {option.label}
                    </Radio.Button>
                  ))}
                </Radio.Group>
              </Form.Item>
            </>
          ) : null}

          {error ? <Alert className="auth-alert" message={error} type="error" showIcon /> : null}

          <Button block htmlType="submit" loading={isSubmitting} size="large" type="primary">
            {isSubmitting ? "处理中..." : mode === "login" ? "登录" : "注册并进入"}
          </Button>
        </Form>
      </Card>
    </main>
  );
}
