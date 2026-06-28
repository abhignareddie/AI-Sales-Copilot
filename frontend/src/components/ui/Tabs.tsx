interface TabsProps {
  tabs: { id: string; label: string }[];
  active: string;
  onChange: (id: string) => void;
}

export const Tabs = ({ tabs, active, onChange }: TabsProps) => (
  <div className="flex border-b border-gray-200 dark:border-gray-800 overflow-x-auto">
    {tabs.map(tab => (
      <button
        key={tab.id}
        onClick={() => onChange(tab.id)}
        className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
          active === tab.id
            ? 'border-blue-600 text-blue-600 dark:text-blue-400'
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        }`}
      >
        {tab.label}
      </button>
    ))}
  </div>
);
