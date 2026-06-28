import { Link } from 'react-router-dom';
import { CheckCircle, MessageSquare, XCircle } from 'lucide-react';
import { ConfidenceBar } from '../ui/ConfidenceBar';
import { getPriorityStyle, getStatusStyle } from '../../lib/utils';
import type { Recommendation } from '../../types';

interface RecommendationCardProps {
  rec: Recommendation;
  onAccept?: () => void;
  onReject?: () => void;
  onFeedback?: () => void;
  showActions?: boolean;
}

export const RecommendationCard = ({ rec, onAccept, onReject, onFeedback, showActions = true }: RecommendationCardProps) => (
  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm hover:shadow-md transition space-y-4">
    <div className="flex items-start justify-between gap-4">
      <div className="flex-1">
        <Link to={`/recommendations/${rec.id}`} className="text-xs text-blue-600 dark:text-blue-400 font-bold uppercase hover:underline">
          Recommendation #{rec.id}
        </Link>
        <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 mt-1">{rec.title || rec.recommendation}</h3>
        <p className="text-sm text-gray-500">{rec.company || `Customer #${rec.customer_id}`}</p>
      </div>
      <div className="flex flex-col items-end gap-1">
        <span className={getPriorityStyle(rec.priority || 'medium')}>{(rec.priority || 'medium').toUpperCase()}</span>
        <span className={getStatusStyle(rec.status)}>{rec.status}</span>
      </div>
    </div>

    <ConfidenceBar value={rec.confidence} />

    <div className="p-3 bg-gray-50 dark:bg-gray-800/40 rounded-lg text-sm text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-800">
      {rec.recommendation}
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
      <div className="p-3 border border-gray-100 dark:border-gray-800 rounded-lg">
        <span className="text-gray-500">Business Impact</span>
        <p className="font-semibold text-gray-800 dark:text-gray-200 mt-1">{rec.business_impact || 'Pipeline acceleration'}</p>
      </div>
      <div className="p-3 border border-gray-100 dark:border-gray-800 rounded-lg">
        <span className="text-gray-500">Projected ROI</span>
        <p className="font-bold text-emerald-500 mt-1">${rec.roi?.toLocaleString() || '—'}</p>
      </div>
      <div className="p-3 border border-gray-100 dark:border-gray-800 rounded-lg">
        <span className="text-gray-500">Suggested Action</span>
        <p className="font-medium text-gray-700 dark:text-gray-300 mt-1 truncate">{rec.suggested_action || rec.recommendation}</p>
      </div>
    </div>

    {rec.evidence && (
      <p className="text-xs text-gray-500 border-l-2 border-amber-400 pl-3">{rec.evidence}</p>
    )}

    {showActions && rec.status === 'Pending Review' && (
      <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-100 dark:border-gray-800">
        {onFeedback && (
          <button onClick={onFeedback} className="px-3 py-1.5 text-xs font-semibold text-gray-600 flex items-center gap-1 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg">
            <MessageSquare className="h-3.5 w-3.5" /> Feedback
          </button>
        )}
        {onReject && (
          <button onClick={onReject} className="px-3 py-1.5 border border-red-200 text-red-600 rounded-lg text-xs font-semibold flex items-center gap-1 hover:bg-red-50 dark:hover:bg-red-950/20">
            <XCircle className="h-3.5 w-3.5" /> Reject
          </button>
        )}
        {onAccept && (
          <button onClick={onAccept} className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow">
            <CheckCircle className="h-3.5 w-3.5" /> Accept
          </button>
        )}
      </div>
    )}
  </div>
);
