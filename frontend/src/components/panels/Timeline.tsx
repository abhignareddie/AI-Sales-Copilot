import { formatRelative } from '../../lib/utils';
import type { TimelineItem } from '../../types';

interface TimelineProps {
  items: TimelineItem[];
}

export const Timeline = ({ items }: TimelineProps) => (
  <div className="relative space-y-0">
    {items.map((item, idx) => (
      <div key={item.id} className="flex gap-4 pb-6 last:pb-0">
        <div className="flex flex-col items-center">
          <div className="h-3 w-3 rounded-full bg-blue-500 ring-4 ring-blue-100 dark:ring-blue-900/30" />
          {idx < items.length - 1 && <div className="w-0.5 flex-1 bg-gray-200 dark:bg-gray-700 mt-1" />}
        </div>
        <div className="flex-1 pb-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">{item.title}</p>
            <span className="text-xs text-gray-400">{formatRelative(item.timestamp)}</span>
          </div>
          {item.description && <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{item.description}</p>}
          <span className="inline-block mt-1 text-[10px] uppercase font-bold text-blue-600 dark:text-blue-400">{item.type}</span>
        </div>
      </div>
    ))}
  </div>
);
