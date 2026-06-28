import type { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  color?: string;
  loading?: boolean;
}

export const StatCard = ({ title, value, description, icon: Icon, color = 'text-blue-500 bg-blue-50 dark:bg-blue-950/20', loading }: StatCardProps) => (
  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm hover:shadow-md transition">
    <div className="flex items-center justify-between mb-3">
      <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">{title}</span>
      <div className={cn('p-2 rounded-lg', color)}>
        <Icon className="h-5 w-5" />
      </div>
    </div>
    {loading ? (
      <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded animate-pulse w-3/4" />
    ) : (
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">{value}</h2>
    )}
    {description && <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>}
  </div>
);
