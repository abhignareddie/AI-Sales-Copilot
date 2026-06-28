import { useQuery } from '@tanstack/react-query';
import { History } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { Timeline } from '../components/panels/Timeline';
import { auditService } from '../services/auditService';

export const AuditLogsPage = () => {
  const { data: logs, isLoading } = useQuery({ queryKey: ['audit-logs'], queryFn: () => auditService.list() });

  const timelineItems = (logs || []).map(l => ({
    id: l.id,
    timestamp: l.timestamp,
    title: `${l.action.toUpperCase()} — ${l.entity}${l.entity_id ? ` #${l.entity_id}` : ''}`,
    description: l.description || `User ${l.user_name || l.user_id || 'System'} performed ${l.action} on ${l.entity}`,
    type: l.entity,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Audit Logs" description="Read-only timeline of all platform actions and changes." />

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <History className="h-5 w-5 text-blue-500" />
          <h3 className="font-semibold">Activity Timeline</h3>
          <span className="text-xs text-gray-400 ml-auto">Read-only</span>
        </div>
        {isLoading ? <LoadingSkeleton rows={6} /> : timelineItems.length ? <Timeline items={timelineItems} /> : <p className="text-sm text-gray-500">No audit logs found.</p>}
      </div>
    </div>
  );
};
