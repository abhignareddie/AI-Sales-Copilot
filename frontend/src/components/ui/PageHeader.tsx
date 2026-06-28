interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export const PageHeader = ({ title, description, actions }: PageHeaderProps) => (
  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h1>
      {description && <p className="text-gray-500 text-sm mt-1">{description}</p>}
    </div>
    {actions && <div className="flex items-center gap-2 flex-wrap">{actions}</div>}
  </div>
);
