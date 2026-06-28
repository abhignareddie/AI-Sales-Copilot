import { FileText } from 'lucide-react';

interface EvidencePanelProps {
  evidence?: string | null;
  documents?: string[];
}

export const EvidencePanel = ({ evidence, documents }: EvidencePanelProps) => (
  <div className="space-y-4">
    {evidence && (
      <div className="p-4 bg-gray-50 dark:bg-gray-800/40 rounded-lg border border-gray-200 dark:border-gray-800">
        <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Supporting Evidence</h4>
        <p className="text-sm text-gray-700 dark:text-gray-300">{evidence}</p>
      </div>
    )}
    {documents && documents.length > 0 && (
      <div>
        <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Retrieved Documents</h4>
        <div className="space-y-2">
          {documents.map(doc => (
            <div key={doc} className="flex items-center gap-2 p-2 bg-blue-50 dark:bg-blue-950/20 rounded-lg text-sm">
              <FileText className="h-4 w-4 text-blue-600" />
              <span className="text-gray-800 dark:text-gray-200">{doc}</span>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);
