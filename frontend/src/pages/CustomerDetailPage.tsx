import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft } from 'lucide-react';
import { Tabs } from '../components/ui/Tabs';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { Timeline } from '../components/panels/Timeline';
import { RecommendationCard } from '../components/cards/RecommendationCard';
import { customerService } from '../services/customerService';
import { meetingService } from '../services/meetingService';
import { emailService } from '../services/emailService';
import { ticketService } from '../services/ticketService';
import { recommendationService } from '../services/recommendationService';
import { memoryService } from '../services/memoryService';
import { auditService } from '../services/auditService';
import { formatCurrency, formatDate } from '../lib/utils';

const DETAIL_TABS = [
  { id: 'overview', label: 'Overview & Health' },
  { id: 'meetings', label: 'Meetings' },
  { id: 'emails', label: 'Emails' },
  { id: 'tickets', label: 'Support Tickets' },
  { id: 'recommendations', label: 'AI Recommendations' },
  { id: 'memory', label: 'Memory' },
  { id: 'audit', label: 'Audit Logs' },
];

export const CustomerDetailPage = () => {
  const { id } = useParams();
  const customerId = Number(id);
  const [tab, setTab] = useState('overview');

  const { data: customer, isLoading } = useQuery({ queryKey: ['customer', customerId], queryFn: () => customerService.get(customerId), enabled: !!customerId });
  const { data: meetings } = useQuery({ queryKey: ['meetings'], queryFn: () => meetingService.list() });
  const { data: emails } = useQuery({ queryKey: ['emails'], queryFn: () => emailService.list() });
  const { data: tickets } = useQuery({ queryKey: ['tickets'], queryFn: () => ticketService.list() });
  const { data: recs } = useQuery({ queryKey: ['recs', customerId], queryFn: () => recommendationService.getByCustomer(customerId), enabled: !!customerId });
  const { data: timeline } = useQuery({ queryKey: ['timeline', customerId], queryFn: () => memoryService.getTimeline(customerId), enabled: !!customerId });
  const { data: auditLogs } = useQuery({ queryKey: ['audit-logs'], queryFn: () => auditService.list() });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!customer) return <p className="text-gray-500">Customer not found.</p>;

  const customerMeetings = meetings?.filter(m => m.customer_id === customerId) || [];
  const customerEmails = emails?.filter(e => e.customer_id === customerId) || [];
  const customerTickets = tickets?.filter(t => t.customer_id === customerId) || [];
  const customerAudits = auditLogs?.filter(a => a.entity === 'customer' && a.entity_id === customerId) || [];

  // Derived metrics for health intelligence dashboard
  const health = customer.health_score || 50;
  const renewalProb = health > 70 ? 92 : health > 40 ? 74 : 38;
  const upsellOpportunity = customer.annual_revenue ? customer.annual_revenue * 0.15 : 25000;
  const engagementIndex = Math.min(100, Math.max(10, customerMeetings.length * 15 + customerEmails.length * 5));
  const supportBurden = customerTickets.length > 5 ? 'High' : customerTickets.length > 2 ? 'Medium' : 'Low';
  const sponsorPresent = customerMeetings.some(m => m.title.toLowerCase().includes('vp') || m.title.toLowerCase().includes('exec')) ? 'Yes' : 'No';

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to="/customers" className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 gap-1"><ArrowLeft className="h-4 w-4" /> Back to Customers</Link>

      {/* Main Profile Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <span className="text-xs text-blue-200 uppercase font-bold tracking-wider">Account Intelligence Control</span>
            <h1 className="text-2xl font-bold mt-1">{customer.company_name}</h1>
            <p className="text-blue-100 text-sm mt-0.5">{customer.contact_person} · {customer.email}</p>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold backdrop-blur-sm">ARR: {formatCurrency(customer.annual_revenue)}</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold backdrop-blur-sm capitalize">Stage: {customer.current_stage}</span>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm overflow-hidden">
        <Tabs tabs={DETAIL_TABS} active={tab} onChange={setTab} />
        <div className="p-6">
          {tab === 'overview' && (
            <div className="space-y-8">
              {/* Executive Health Gauges Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                {/* Health Score Gauge */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800/40 border border-gray-150 dark:border-gray-800 rounded-xl flex flex-col justify-between items-center text-center">
                  <span className="text-xs font-bold text-gray-450 dark:text-gray-400 uppercase tracking-wider">Customer Health</span>
                  <div className="relative flex items-center justify-center my-4 h-24 w-24">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="48" cy="48" r="40" stroke="#e5e7eb" strokeWidth="8" fill="transparent" className="dark:stroke-gray-800" />
                      <circle cx="48" cy="48" r="40" stroke={health > 70 ? '#10b981' : health > 40 ? '#f59e0b' : '#ef4444'} strokeWidth="8" fill="transparent" strokeDasharray="251" strokeDashoffset={251 - (251 * health) / 100} className="transition-all duration-500" />
                    </svg>
                    <span className="absolute text-lg font-black text-gray-850 dark:text-gray-100">{health}%</span>
                  </div>
                  <span className="text-[10px] text-gray-500">Based on recent ticket resolution rate</span>
                </div>

                {/* Renewal Probability Ring */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800/40 border border-gray-150 dark:border-gray-800 rounded-xl flex flex-col justify-between items-center text-center">
                  <span className="text-xs font-bold text-gray-450 dark:text-gray-400 uppercase tracking-wider">Renewal Probability</span>
                  <div className="relative flex items-center justify-center my-4 h-24 w-24">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="48" cy="48" r="40" stroke="#e5e7eb" strokeWidth="8" fill="transparent" className="dark:stroke-gray-800" />
                      <circle cx="48" cy="48" r="40" stroke="#3b82f6" strokeWidth="8" fill="transparent" strokeDasharray="251" strokeDashoffset={251 - (251 * renewalProb) / 100} className="transition-all duration-500" />
                    </svg>
                    <span className="absolute text-lg font-black text-gray-850 dark:text-gray-100">{renewalProb}%</span>
                  </div>
                  <span className="text-[10px] text-gray-500">Predicted churn risk analysis</span>
                </div>

                {/* Engagement Index Ring */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800/40 border border-gray-150 dark:border-gray-800 rounded-xl flex flex-col justify-between items-center text-center">
                  <span className="text-xs font-bold text-gray-450 dark:text-gray-400 uppercase tracking-wider">Engagement Index</span>
                  <div className="relative flex items-center justify-center my-4 h-24 w-24">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="48" cy="48" r="40" stroke="#e5e7eb" strokeWidth="8" fill="transparent" className="dark:stroke-gray-800" />
                      <circle cx="48" cy="48" r="40" stroke="#8b5cf6" strokeWidth="8" fill="transparent" strokeDasharray="251" strokeDashoffset={251 - (251 * engagementIndex) / 100} className="transition-all duration-500" />
                    </svg>
                    <span className="absolute text-lg font-black text-gray-850 dark:text-gray-100">{engagementIndex}%</span>
                  </div>
                  <span className="text-[10px] text-gray-500">Meetings & email frequencies</span>
                </div>

                {/* Support Burden card */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800/40 border border-gray-150 dark:border-gray-800 rounded-xl flex flex-col justify-between items-center text-center">
                  <span className="text-xs font-bold text-gray-450 dark:text-gray-400 uppercase tracking-wider">Support Burden</span>
                  <div className="my-5 space-y-1">
                    <span className={`text-2xl font-black ${
                      supportBurden === 'High' ? 'text-red-500' : supportBurden === 'Medium' ? 'text-amber-500' : 'text-green-500'
                    }`}>{supportBurden}</span>
                    <p className="text-[10px] text-gray-550 block">Open tickets: {customerTickets.length}</p>
                  </div>
                  <span className="text-[10px] text-gray-500">Impact on engineer bandwidth</span>
                </div>
              </div>

              {/* Extended Customer Context Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-100 dark:border-gray-800 text-sm">
                <div className="space-y-4">
                  <h3 className="font-bold text-base text-gray-850 dark:text-gray-100">Enterprise Profile</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div><span className="text-gray-450 text-xs">Primary Contact</span><p className="font-semibold text-gray-800 dark:text-gray-200 mt-0.5">{customer.contact_person}</p></div>
                    <div><span className="text-gray-450 text-xs">Industry Segment</span><p className="font-semibold text-gray-800 dark:text-gray-200 mt-0.5">{customer.industry || '—'}</p></div>
                    <div><span className="text-gray-450 text-xs">Company Size</span><p className="font-semibold text-gray-800 dark:text-gray-200 mt-0.5">{customer.company_size || '—'} Employees</p></div>
                    <div><span className="text-gray-450 text-xs">Annual Contract Value</span><p className="font-semibold text-emerald-500 mt-0.5">{formatCurrency(customer.annual_revenue)}</p></div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-bold text-base text-gray-850 dark:text-gray-100">Account Health Signals</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div><span className="text-gray-450 text-xs">Executive Sponsor present</span><p className="font-semibold text-gray-800 dark:text-gray-200 mt-0.5">{sponsorPresent}</p></div>
                    <div><span className="text-gray-450 text-xs">Projected Expansion Value</span><p className="font-semibold text-blue-600 dark:text-blue-400 mt-0.5">{formatCurrency(upsellOpportunity)}</p></div>
                    <div><span className="text-gray-450 text-xs">Assigned Sales Rep</span><p className="font-semibold text-gray-800 dark:text-gray-200 mt-0.5">{customer.assigned_sales_rep || 'Unassigned'}</p></div>
                    <div><span className="text-gray-450 text-xs">Support Tickets</span><p className="font-semibold text-gray-800 dark:text-gray-200 mt-0.5">{customerTickets.length} Open Issues</p></div>
                  </div>
                </div>

                {customer.notes && (
                  <div className="md:col-span-2 p-3 bg-gray-50 dark:bg-gray-800/40 border border-gray-150 dark:border-gray-850 rounded-lg">
                    <span className="text-gray-450 text-xs font-bold block mb-1">Internal Notes</span>
                    <p className="text-gray-650 dark:text-gray-400 text-xs leading-relaxed">{customer.notes}</p>
                  </div>
                )}
              </div>
            </div>
          )}
          {tab === 'meetings' && (
            customerMeetings.length ? (
              <div className="space-y-4">
                {customerMeetings.map(m => (
                  <div key={m.id} className="p-4 border border-gray-150 dark:border-gray-850 rounded-xl space-y-2 hover:shadow-sm transition">
                    <div className="flex justify-between items-center">
                      <h4 className="font-bold text-sm text-gray-900 dark:text-gray-100">{m.title}</h4>
                      <span className="text-xs text-gray-400">{formatDate(m.meeting_date)}</span>
                    </div>
                    <p className="text-xs text-gray-550 leading-relaxed">{m.summary}</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No meetings recorded.</p>
          )}
          {tab === 'emails' && (
            customerEmails.length ? (
              <div className="space-y-4">
                {customerEmails.map(e => (
                  <div key={e.id} className="p-4 border border-gray-150 dark:border-gray-850 rounded-xl space-y-2 hover:shadow-sm transition">
                    <div className="flex justify-between items-center">
                      <h4 className="font-bold text-sm text-gray-900 dark:text-gray-100">{e.subject}</h4>
                      <span className="text-xs text-gray-400">{formatDate(e.created_at)}</span>
                    </div>
                    <p className="text-xs text-gray-500 font-semibold">{e.sender} → {e.receiver}</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No emails recorded.</p>
          )}
          {tab === 'tickets' && (
            customerTickets.length ? (
              <div className="space-y-4">
                {customerTickets.map(t => (
                  <div key={t.id} className="p-4 border border-gray-150 dark:border-gray-850 rounded-xl space-y-2 hover:shadow-sm transition flex justify-between items-center">
                    <div>
                      <h4 className="font-bold text-sm text-gray-900 dark:text-gray-100">{t.ticket_number}: {t.issue}</h4>
                      <span className="text-xs text-gray-450 block mt-1">Created: {formatDate(t.created_at)}</span>
                    </div>
                    <span className="px-2.5 py-1 bg-amber-50 dark:bg-amber-950/20 text-amber-600 rounded-lg text-xs font-semibold capitalize">{t.priority}</span>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No support tickets.</p>
          )}
          {tab === 'recommendations' && (
            <div className="space-y-4">
              {(recs || []).map(r => <RecommendationCard key={r.id} rec={r} showActions={false} />)}
              {!recs?.length && <p className="text-sm text-gray-500">No recommendations generated.</p>}
            </div>
          )}
          {tab === 'memory' && (
            timeline?.length ? <Timeline items={timeline} /> : <p className="text-sm text-gray-500">No memory entries found.</p>
          )}
          {tab === 'audit' && (
            customerAudits.length ? (
              <div className="space-y-3">
                {customerAudits.map(a => (
                  <div key={a.id} className="p-3 border border-gray-100 dark:border-gray-850 rounded-xl text-sm hover:bg-gray-50/50 transition">
                    <p className="font-bold text-gray-800 dark:text-gray-200 capitalize">{a.action} — {a.entity}</p>
                    <p className="text-xs text-gray-500 mt-1">{a.description || formatDate(a.timestamp)}</p>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-gray-500">No audit logs for this customer.</p>
          )}
        </div>
      </div>
    </div>
  );
};
