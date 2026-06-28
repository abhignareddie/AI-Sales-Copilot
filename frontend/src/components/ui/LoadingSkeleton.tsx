interface LoadingSkeletonProps {
  rows?: number;
}

export const LoadingSkeleton = ({ rows = 5 }: LoadingSkeletonProps) => (
  <div className="p-6 space-y-4">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="h-12 bg-gray-200 dark:bg-gray-800 rounded animate-pulse" style={{ width: `${100 - i * 8}%` }} />
    ))}
  </div>
);

export const CardSkeleton = () => (
  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm space-y-3">
    <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded animate-pulse w-1/3" />
    <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded animate-pulse w-2/3" />
    <div className="h-3 bg-gray-200 dark:bg-gray-800 rounded animate-pulse w-full" />
  </div>
);
