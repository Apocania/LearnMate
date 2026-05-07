type PageHeaderProps = {
  title: string;
  description?: string;
};

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="page-header">
      <h2 className="page-title">{title}</h2>
      {description ? <p className="page-description">{description}</p> : null}
    </header>
  );
}

