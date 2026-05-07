type EmptyStateProps = {
  title: string;
  description?: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      {description ? <p className="page-description">{description}</p> : null}
    </section>
  );
}

