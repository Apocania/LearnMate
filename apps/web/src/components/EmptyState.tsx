import { Empty } from "antd";

type EmptyStateProps = {
  title: string;
  description?: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return <Empty className="empty-state" description={description ?? title} />;
}
