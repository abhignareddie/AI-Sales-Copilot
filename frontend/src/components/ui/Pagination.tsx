import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const Pagination = ({ page, totalPages, onPageChange }: PaginationProps) => {
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 dark:border-gray-800">
      <span className="text-xs text-gray-500">Page {page} of {totalPages}</span>
      <div className="flex space-x-1">
        <button
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="p-1.5 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <button
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          className="p-1.5 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
