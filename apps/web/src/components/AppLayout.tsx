import {
  BookOutlined,
  BulbOutlined,
  MessageOutlined,
  RobotOutlined,
  UserOutlined
} from "@ant-design/icons";
import { Button, Layout, Typography } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { clearStoredSession } from "../shared/utils/currentUser";
import { useCurrentUser } from "../shared/utils/useCurrentUser";

const navItems = [
  { key: "/courses", icon: <BookOutlined />, label: "课程中心" },
  { key: "/forum", icon: <MessageOutlined />, label: "讨论交流" },
  { key: "/assistant", icon: <RobotOutlined />, label: "AI伴学" },
  { key: "/reports/me", icon: <UserOutlined />, label: "个人中心" }
];

export function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const selectedKey = navItems.find((item) => location.pathname.startsWith(item.key))?.key ?? "";

  function handleLogout() {
    clearStoredSession();
    navigate("/login");
  }

  return (
    <Layout className="app-shell">
      <Layout.Header className="top-header">
        <button className="brand-button" type="button" onClick={() => navigate("/")}>
          <span className="brand-mascot">
            <BulbOutlined />
          </span>
          <span className="brand-copy">
            <Typography.Text className="brand-title">LearnMate</Typography.Text>
            <Typography.Text className="brand-subtitle">快乐学习伙伴</Typography.Text>
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
              <span className="user-pill">
                {currentUser.username} · {currentUser.role === "mentor" ? "伴学师" : "学生"}
              </span>
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
    </Layout>
  );
}
