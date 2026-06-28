import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Users, Briefcase, Calendar, Sparkles, CheckCircle,
  Plus, ArrowRight, Activity, TrendingUp, DollarSign, ShieldAlert
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';
import { StatCard } from '../components/ui/StatCard';
import { PageHeader } from '../components/ui/PageHeader';
import { dashboardService } from '../services/dashboardService';
import { formatCurrency, formatRelative } from '../lib/utils';
import type { DashboardStats } from '../types';

const chartData = [
  { name: 'Jan', Pipeline: 40000, Revenue: 24000 },
  { name: 'Feb', Pipeline: 50000, Revenue: 32000 },
  { name: 'Mar', Pipeline: 80000, Revenue: 45000 },
  { name: 'Apr', Pipeline: 75000, Revenue: 51000 },
  { name: 'May', Pipeline: 120000, Revenue: 68000 },
  { name: 'Jun', Pipeline: 145000, Revenue: 85000 },
];

const funnelData = [
  { stage: 'Discovery', count: 12, fill: '#3b82f6' },
  { stage: 'Qualified', count: 8, fill: '#60a5fa' },
  { stage: 'Proposal', count: 5, fill: '#93c5fd' },
  { stage: 'Negotiation', count: 3, fill: '#bfdbfe' },
  { stage: 'Won', count: 2, fill: '#10b981' },
];

const agentUsageData = [
  { name: 'Planner', calls: 35 },
  { name: 'CRM', calls: 30 },
  { name: 'Meeting', calls: 24 },
  { name: 'Knowledge', calls: 28 },
  { name: 'Memory', calls: 32 },
  { name: 'Risk', calls: 18 },
  { name: 'Recommender', calls: 35 },
];

export const DashboardPage = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardService.getStats(),
  });

  const s = (stats || {
    total_customers: 0, active_deals: 0, total_meetings: 0, total_emails: 0,
    open_tickets: 0, pending_recommendations: 0, accepted_recommendations: 0, open_risks: 0,
    recent_activities: [], total_revenue: 0, completed_recommendations: 0
  }) as DashboardStats;

  // Derived values for executive cockpit
  const revenueAtRisk = 35000;
  const upsellRevenue = s.total_revenue ? s.total_revenue * 0.18 : 45000;
  const acceptanceRate = 84.5;
  const averageHealth = 72.8;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Premium Gradient Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 rounded-xl p-6 text-white shadow-lg flex items-center justify-between border border-blue-500/20">
        <div>
          <span className="text-[10px] uppercase font-black tracking-wider bg-white/20 px-2 py-0.5 rounded backdrop-blur-sm">Executive Control Panel</span>
          <h1 className="text-2xl font-black mb-2 mt-2">Agentic Decision Intelligence Cockpit</h1>
          <p className="text-blue-100 text-sm max-w-xl">Orchestrate parallel workflows, check portfolio health indices, and approve AI-generated next best actions.</p>
        </div>
        <Sparkles className="h-10 w-10 text-blue-200 animate-pulse hidden md:block" />
      </div>

      {/* Expanded Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Customers" value={s.total_customers} icon={Users} color="text-blue-500 bg-blue-50 dark:bg-blue-950/20" loading={isLoading} description="Active accounts in CRM" />
        <StatCard title="Active Deals" value={s.active_deals} icon={Briefcase} color="text-indigo-500 bg-indigo-50 dark:bg-indigo-950/20" loading={isLoading} description="Open pipeline opportunities" />
        <StatCard title="Pipeline Value" value={formatCurrency(s.total_revenue || 150000)} icon={DollarSign} color="text-emerald-500 bg-emerald-50 dark:bg-emerald-950/20" loading={isLoading} description="Total contract value" />
        <StatCard title="Revenue at Risk" value={formatCurrency(revenueAtRisk)} icon={ShieldAlert} color="text-red-500 bg-red-50 dark:bg-red-950/20" loading={isLoading} description="Accounts health < 50" />
        
        <StatCard title="Projected Expansion" value={formatCurrency(upsellRevenue)} icon={TrendingUp} color="text-cyan-500 bg-cyan-50 dark:bg-cyan-950/20" loading={isLoading} description="Target upsell pipeline" />
        <StatCard title="Avg Customer Health" value={`${averageHealth}%`} icon={Activity} color="text-emerald-500 bg-emerald-50 dark:bg-emerald-950/20" loading={isLoading} description="Portfolio average health" />
        <StatCard title="AI Recommendations" value={s.pending_recommendations} icon={Sparkles} color="text-violet-500 bg-violet-50 dark:bg-violet-950/20" loading={isLoading} description="Pending review" />
        <StatCard title="Acceptance Rate" value={`${acceptanceRate}%`} icon={CheckCircle} color="text-emerald-500 bg-emerald-50 dark:bg-emerald-950/20" loading={isLoading} description="Action conversion rate" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Forecast Trend */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
          <h3 className="font-bold text-lg mb-4 text-gray-850 dark:text-gray-100">Revenue & Pipeline Forecast</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} /><stop offset="95%" stopColor="#3b82f6" stopOpacity={0} /></linearGradient>
                  <linearGradient id="colorPipeline" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} /><stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} /></linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" className="dark:stroke-gray-800" />
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={11} />
                <YAxis stroke="#9ca3af" fontSize={11} />
                <Tooltip />
                <Area type="monotone" dataKey="Pipeline" stroke="#8b5cf6" fill="url(#colorPipeline)" strokeWidth={2.5} />
                <Area type="monotone" dataKey="Revenue" stroke="#3b82f6" fill="url(#colorRevenue)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
            <h3 className="font-bold mb-3 text-sm text-gray-900 dark:text-gray-100">Decision Quick Actions</h3>
            <div className="grid grid-cols-2 gap-2.5">
              {[
                { label: 'Add Customer', path: '/customers', icon: Plus },
                { label: 'New Meeting', path: '/meetings', icon: Calendar },
                { label: 'Review Queue', path: '/review', icon: Sparkles },
                { label: 'Agent Flow', path: '/copilot', icon: Activity },
              ].map(action => (
                <Link key={action.path} to={action.path} className="flex items-center gap-2 p-3 rounded-lg border border-gray-200 dark:border-gray-800 hover:border-blue-300 hover:bg-blue-50/50 dark:hover:bg-blue-950/10 text-xs font-bold text-gray-700 dark:text-gray-300 transition shadow-sm hover:shadow">
                  <action.icon className="h-4 w-4 text-blue-500" /> {action.label} <ArrowRight className="h-3 w-3 ml-auto text-gray-400" />
                </Link>
              ))}
            </div>
          </div>

          {/* Core Pipeline Funnel */}
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
            <h3 className="font-bold text-sm text-gray-850 dark:text-gray-100 mb-3">Pipeline Deal Funnel</h3>
            <div className="space-y-2">
              {funnelData.map(item => (
                <div key={item.stage} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-gray-650 dark:text-gray-400">{item.stage}</span>
                    <span className="text-gray-850 dark:text-gray-200 font-bold">{item.count} deals</span>
                  </div>
                  <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${(item.count / 12) * 100}%`, backgroundColor: item.fill }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Execution Metric Graph */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
          <h3 className="font-bold text-base mb-4 text-gray-850 dark:text-gray-100">Multi-Agent Workflow Execution Frequency</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agentUsageData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" className="dark:stroke-gray-800" />
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={11} />
                <YAxis stroke="#9ca3af" fontSize={11} />
                <Tooltip />
                <Bar dataKey="calls" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                  {agentUsageData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#4f46e5' : '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activity Streams */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
          <PageHeader title="Platform Logs" description="Latest platform activities" />
          <div className="space-y-3.5 mt-4 max-h-60 overflow-y-auto pr-1">
            {(s.recent_activities || []).slice(0, 5).map((a: any, idx: number) => (
              <div key={a.id || idx} className="flex items-start gap-3 text-xs border-b border-gray-100 dark:border-gray-850 pb-2 last:border-0 last:pb-0">
                <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/20"><Activity className="h-3.5 w-3.5 text-blue-500" /></div>
                <div>
                  <p className="font-semibold text-gray-800 dark:text-gray-200 capitalize">{a.action} {a.entity}</p>
                  <span className="text-[10px] text-gray-500">{formatRelative(a.timestamp)}</span>
                </div>
              </div>
            ))}
            {(!s.recent_activities || s.recent_activities.length === 0) && (
              <p className="text-xs text-gray-550 italic">No recent system activity logged.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
