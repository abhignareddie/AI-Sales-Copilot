import { formatDate } from '../../lib/utils';
import type { Meeting } from '../../types';

interface MeetingCardProps {
  meeting: Meeting;
  onView?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export const MeetingCard = ({ meeting, onView, onEdit, onDelete }: MeetingCardProps) => (
  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm space-y-3">
    <div className="flex items-start justify-between">
      <div>
        <h3 className="font-bold text-gray-900 dark:text-gray-100">{meeting.title}</h3>
        <p className="text-xs text-gray-500">{meeting.customer_name || `Customer #${meeting.customer_id}`}</p>
      </div>
      <span className="text-xs text-gray-400">{formatDate(meeting.meeting_date)}</span>
    </div>
    {meeting.participants && <p className="text-xs text-gray-500">Participants: {meeting.participants}</p>}
    {meeting.summary && <p className="text-sm text-gray-700 dark:text-gray-300">{meeting.summary}</p>}
    {meeting.transcript && (
      <p className="text-xs text-gray-400 italic truncate border-l-2 border-blue-300 pl-2">
        {meeting.transcript.slice(0, 120)}...
      </p>
    )}
    <div className="flex justify-end gap-2 pt-2">
      {onView && <button onClick={onView} className="px-3 py-1 text-xs font-semibold text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/20 rounded-lg">View</button>}
      {onEdit && <button onClick={onEdit} className="px-3 py-1 text-xs font-semibold text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg">Edit</button>}
      {onDelete && <button onClick={onDelete} className="px-3 py-1 text-xs font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg">Delete</button>}
    </div>
  </div>
);
