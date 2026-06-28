interface ReasoningPanelProps {
  reasoning?: string;
  steps?: string[];
}

export const ReasoningPanel = ({ reasoning, steps }: ReasoningPanelProps) => (
  <div className="space-y-4">
    {reasoning && (
      <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-lg border border-blue-100 dark:border-blue-900/30">
        <h4 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase mb-2">AI Reasoning Chain</h4>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{reasoning}</p>
      </div>
    )}
    {steps && steps.length > 0 && (
      <ol className="space-y-2">
        {steps.map((step, i) => (
          <li key={i} className="flex gap-3 text-sm">
            <span className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center">{i + 1}</span>
            <span className="text-gray-700 dark:text-gray-300 pt-0.5">{step}</span>
          </li>
        ))}
      </ol>
    )}
  </div>
);
