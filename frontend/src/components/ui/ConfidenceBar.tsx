interface ConfidenceBarProps {
  value: number;
  showLabel?: boolean;
}

export const ConfidenceBar = ({ value, showLabel = true }: ConfidenceBarProps) => {
  const pct = Math.round(value * 100);
  const color = pct >= 85 ? 'bg-green-500' : pct >= 65 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex justify-between text-xs">
          <span className="text-gray-500 dark:text-gray-400">Confidence</span>
          <span className="font-semibold text-gray-900 dark:text-gray-100">{pct}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded-full overflow-hidden">
        <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
};
