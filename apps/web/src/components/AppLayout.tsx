import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "学习首页" },
  { to: "/courses", label: "课程中心" },
  { to: "/forum", label: "论坛交流" },
  { to: "/assistant", label: "AI 助教" },
  { to: "/reports/me", label: "学习报告" }
];

export function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <h1 className="brand-title">智能伴学系统</h1>
          <p className="brand-subtitle">Guochuang Learning</p>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <NavLink className="nav-link" key={item.to} to={item.to}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}

