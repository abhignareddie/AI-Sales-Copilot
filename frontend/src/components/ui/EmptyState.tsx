import type { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState = ({ icon: Icon, title, description, action }: EmptyStateProps) => (
  <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
    <div className="p-4 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
      <Icon className="h-8 w-8 text-gray-400" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">{title}</h3>
    {description && <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mb-4">{description}</p>}
    {action}
  </div>
);
