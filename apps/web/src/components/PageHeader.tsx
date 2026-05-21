import { Typography } from "antd";

type PageHeaderProps = {
  title: string;
  description?: string;
  eyebrow?: string;
};

export function PageHeader({ title, description, eyebrow }: PageHeaderProps) {
  return (
    <header className="page-header">
      {eyebrow ? <Typography.Text className="page-eyebrow">{eyebrow}</Typography.Text> : null}
      <Typography.Title className="page-title" level={2}>
        {title}
      </Typography.Title>
      {description ? <Typography.Text type="secondary">{description}</Typography.Text> : null}
    </header>
  );
}
