import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Brain, Mail, Calendar, Sparkles, Search, Info } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Tabs } from '../components/ui/Tabs';
import { Timeline } from '../components/panels/Timeline';
import { customerService } from '../services/customerService';
import { memoryService } from '../services/memoryService';
import { recommendationService } from '../services/recommendationService';
import { meetingService } from '../services/meetingService';
import { emailService } from '../services/emailService';
import { formatDate } from '../lib/utils';

const MEMORY_TABS = [
  { id: 'timeline', label: 'Conversation Timeline' },
  { id: 'meetings', label: 'Previous Meetings' },
  { id: 'emails', label: 'Previous Emails' },
  { id: 'recommendations', label: 'Past Recommendations' },
  { id: 'rules', label: 'Triggered Rules Log' }
];

export const MemoryPage = () => {
  const [customerId, setCustomerId] = useState(1);
  const [tab, setTab] = useState('timeline');
  const [filterType, setFilterType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: customers } = useQuery({ queryKey: ['customers-all'], queryFn: () => customerService.list({ page_size: 100 }) });
  const { data: timeline } = useQuery({ queryKey: ['timeline', customerId], queryFn: () => memoryService.getTimeline(customerId) });
  const { data: meetings } = useQuery({ queryKey: ['meetings'], queryFn: () => meetingService.list() });
  const { data: emails } = useQuery({ queryKey: ['emails'], queryFn: () => emailService.list() });
  const { data: recs } = useQuery({ queryKey: ['recs', customerId], queryFn: () => recommendationService.getByCustomer(customerId) });

  const customerMeetings = meetings?.filter(m => m.customer_id === customerId) || [];
  const customerEmails = emails?.filter(e => e.customer_id === customerId) || [];
  const filteredTimeline = (timeline || []).filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = filterType === 'all' || item.type.toLowerCase() === filterType.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  const ruleLogs = [
    { rule: 'Adoption Decline Alert', timestamp: '2026-06-25T10:00:00Z', trigger: 'Health score drop < 50', type: 'System Rule' },
    { rule: 'High Value ACV Playbook', timestamp: '2026-06-24T14:30:00Z', trigger: 'ARR over $100K threshold', type: 'Sales Governance' },
    { rule: 'SSO Objection Escalation', timestamp: '2026-06-23T09:15:00Z', trigger: 'SSO query found in transcripts', type: 'Compliance Guard' }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader title="Memory Center" description="Enterprise Account Memory — View chronologically structured timeline logs and prior agent actions." />

      {/* Filter and Client Selector panel */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Brain className="h-5 w-5 text-blue-500" />
          <span className="text-xs font-bold text-gray-500 uppercase">Selected Client:</span>
          <select value={customerId} onChange={e => setCustomerId(Number(e.target.value))} className="px-3 py-1.5 bg-gray-50 dark:bg-gray-850 border border-gray-200 dark:border-gray-850 rounded-lg text-xs font-semibold">
            {(customers?.items || []).map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
          </select>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <div className="relative text-xs">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
            <input 
              placeholder="Search timeline..." 
              value={searchQuery} 
              onChange={e => setSearchQuery(e.target.value)} 
              className="pl-8 pr-3 py-2 bg-gray-50 dark:bg-gray-850 border border-gray-200 dark:border-gray-850 rounded-lg text-xs" 
            />
          </div>
          <select value={filterType} onChange={e => setFilterType(e.target.value)} className="px-3 py-2 bg-gray-50 dark:bg-gray-850 border border-gray-200 dark:border-gray-850 rounded-lg text-xs">
            <option value="all">All Events</option>
            <option value="meeting">Meetings</option>
            <option value="email">Emails</option>
            <option value="recommendation">AI Recommendations</option>
          </select>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm">
        <Tabs tabs={MEMORY_TABS} active={tab} onChange={setTab} />
        <div className="p-6">
          {tab === 'timeline' && (
            filteredTimeline.length ? (
              <div className="max-w-xl">
                <Timeline items={filteredTimeline} />
              </div>
            ) : <p className="text-sm text-gray-500">No timeline entries found matching query filters.</p>
          )}

          {tab === 'meetings' && (
            customerMeetings.length ? (
              <div className="space-y-4">
                {customerMeetings.map(m => (
                  <div key={m.id} className="flex items-start gap-4 p-4 border border-gray-150 dark:border-gray-850 rounded-xl hover:shadow-sm transition">
                    <Calendar className="h-5 w-5 text-blue-500 mt-0.5" />
                    <div className="space-y-1">
                      <div className="flex justify-between items-center w-full">
                        <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{m.title}</p>
                        <span className="text-[10px] text-gray-400">{formatDate(m.meeting_date)}</span>
                      </div>
                      <p className="text-xs text-gray-500 leading-relaxed">{m.summary}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No meeting histories logged.</p>
          )}

          {tab === 'emails' && (
            customerEmails.length ? (
              <div className="space-y-4">
                {customerEmails.map(e => (
                  <div key={e.id} className="flex items-start gap-4 p-4 border border-gray-150 dark:border-gray-850 rounded-xl hover:shadow-sm transition">
                    <Mail className="h-5 w-5 text-cyan-500 mt-0.5" />
                    <div className="space-y-1">
                      <div className="flex justify-between items-center w-full">
                        <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{e.subject}</p>
                        <span className="text-[10px] text-gray-400">{formatDate(e.created_at)}</span>
                      </div>
                      <p className="text-xs text-gray-500 font-semibold">{e.sender} → {e.receiver}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No email histories logged.</p>
          )}

          {tab === 'recommendations' && (
            recs?.length ? (
              <div className="space-y-4">
                {recs.map(r => (
                  <div key={r.id} className="flex items-start gap-4 p-4 border border-gray-150 dark:border-gray-850 rounded-xl hover:shadow-sm transition">
                    <Sparkles className="h-5 w-5 text-violet-500 mt-0.5" />
                    <div className="space-y-1">
                      <div className="flex justify-between items-center w-full">
                        <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{r.recommendation}</p>
                        <span className="px-2 py-0.5 bg-gray-50 dark:bg-gray-800 text-[10px] text-gray-400 rounded-lg">{r.status}</span>
                      </div>
                      <p className="text-xs text-gray-500 italic mt-1">ROI: ${r.roi?.toLocaleString()} · Confidence: {(r.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No recommendations logged.</p>
          )}

          {tab === 'rules' && (
            <div className="space-y-4">
              {ruleLogs.map((log, idx) => (
                <div key={idx} className="flex items-start gap-4 p-4 border border-gray-150 dark:border-gray-850 rounded-xl hover:shadow-sm transition">
                  <Info className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div>
                    <div className="flex justify-between items-center w-full">
                      <p className="font-bold text-sm text-gray-900 dark:text-gray-100">{log.rule}</p>
                      <span className="text-[10px] text-gray-400">{formatDate(log.timestamp)}</span>
                    </div>
                    <p className="text-xs text-gray-500"><b>Trigger:</b> {log.trigger} · <b>Category:</b> {log.type}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
