import { Typography } from "antd";

type PageHeaderProps = {
  title: string;
  description?: string;
};

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="page-header">
      <Typography.Title className="page-title" level={2}>
        {title}
      </Typography.Title>
      {description ? <Typography.Text type="secondary">{description}</Typography.Text> : null}
    </header>
  );
}
