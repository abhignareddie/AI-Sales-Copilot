import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowLeft, Brain, Mail, Calendar, FileText, Shield, 
  TrendingUp, CheckCircle, ChevronDown, ChevronUp
} from 'lucide-react';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { recommendationService } from '../services/recommendationService';
import { customerService } from '../services/customerService';
import { getPriorityStyle, getStatusStyle } from '../lib/utils';

export const RecommendationDetailPage = () => {
  const { id } = useParams();
  const recId = Number(id);

  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const { data: rec, isLoading } = useQuery({ queryKey: ['recommendation', recId], queryFn: () => recommendationService.get(recId), enabled: !!recId });
  const { data: customer } = useQuery({ queryKey: ['customer', rec?.customer_id], queryFn: () => customerService.get(rec!.customer_id), enabled: !!rec?.customer_id });

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!rec) return <p className="text-gray-500 text-sm">Recommendation not found.</p>;

  const toggleSection = (section: string) => {
    setExpandedSection(prev => prev === section ? null : section);
  };

  const confidenceBreakdown = [
    { label: 'Meeting Transcript Evidence', value: 80, color: 'bg-purple-500' },
    { label: 'Knowledge Base Alignment', value: 100, color: 'bg-emerald-500' },
    { label: 'Historical Account Memory', value: 70, color: 'bg-cyan-500' },
    { label: 'Triggered Business Rules', value: 90, color: 'bg-blue-500' },
  ];

  const reasoningChain = [
    { agent: 'Planner Agent', action: 'Orchestrated analysis pipeline and determined routing based on customer health decline.' },
    { agent: 'CRM Agent', action: 'Retrieved customer profile: Acme Corporation, ARR $150K, Contract renewal within 30 days.' },
    { agent: 'Meeting Agent', action: 'Scanned latest meeting transcript; flagged VP pricing objections and SSO timeline concerns.' },
    { agent: 'Knowledge Agent', action: 'Matched search tokens with playbook files; extracted premium_pricing_plan.pdf discounts.' },
    { agent: 'Risk Agent', action: 'Flagged customer health drop to 48% (under warning limit of 50%).' },
    { agent: 'Recommendation Agent', action: 'Synthesized prioritized Next Best Action: Schedule immediate VP proposal alignment review.' }
  ];

  const triggeredRules = [
    { title: 'Contract Renewal < 30 Days', desc: 'Fires when customer ARR renewal date is within 30 days. Action: Prioritize sponsor alignment.' },
    { title: 'ARR > $100K High-Value Account', desc: 'Fires for key enterprise accounts. Action: Restrict alternative playbooks to executive escalation.' },
    { title: 'Customer Health Score < 50', desc: 'Fires when adoption or support tickets deteriorate health indicator. Action: Flag account as churn risk.' },
    { title: 'Competitor Mentioned in Transcripts', desc: 'Fired when keywords like Gong, Chorus, or Outreach are detected. Action: Trigger competitive pricing playbook.' }
  ];

  const alternatives = [
    {
      title: 'Top Recommendation: Executive Alignment Review',
      roi: rec.roi || 15000,
      successRate: 94,
      risk: 'Low',
      pros: 'Aligns executive decision maker directly; resolves timeline bottlenecks immediately.',
      cons: 'Requires scheduling availability from VP and account sponsor.',
      reasoning: 'Acme VP raised timeline objections in latest Q2 business review. Direct alignment prevents contract delay.',
      timeline: 'This week'
    },
    {
      title: 'Alternative Action 1: Propose Bundle Discount Playbook',
      roi: 8500,
      successRate: 78,
      risk: 'Medium',
      pros: 'Lowers financial barrier by offering bundle options for SSO modules.',
      cons: 'Reduces short-term ARR expansion yield.',
      reasoning: 'Customer pricing questions were flagged in recent emails. Offering discounting options improves close probability.',
      timeline: 'Next 10 days'
    },
    {
      title: 'Alternative Action 2: Trigger Adoption Audit Review',
      roi: 5000,
      successRate: 65,
      risk: 'Low',
      pros: 'Identifies core adoption issues inside developer team to improve long-term value.',
      cons: 'Does not directly address short-term contract renewal timeline pressure.',
      reasoning: 'Health score has dropped below 50 due to unresolved support tickets. System review repairs health indicators.',
      timeline: 'This month'
    }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to="/review" className="flex items-center text-sm text-gray-600 hover:text-blue-600 gap-1"><ArrowLeft className="h-4 w-4" /> Back to Review Queue</Link>

      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <p className="text-xs text-blue-200 uppercase font-bold tracking-wider">Explainability Center</p>
            <h1 className="text-2xl font-bold mt-1">Recommendation: {rec.title || rec.recommendation}</h1>
            <p className="text-blue-100 text-sm mt-1">{customer?.company_name || rec.company}</p>
          </div>
          <div className="flex flex-row md:flex-col items-center md:items-end gap-2">
            <span className={getPriorityStyle(rec.priority || 'medium')}>{(rec.priority || 'medium').toUpperCase()}</span>
            <span className={getStatusStyle(rec.status)}>{rec.status}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Explainability Breakdown Card */}
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm space-y-6">
            <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-500" /> AI Decision Confidence & Evidence Trace
            </h3>

            {/* Overall Confidence Radar/Bar */}
            <div className="p-4 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-150 dark:border-gray-800">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-bold text-gray-800 dark:text-gray-200">Overall Recommendation Confidence</span>
                <span className="text-lg font-black text-blue-600 dark:text-blue-400">{(rec.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" style={{ width: `${rec.confidence * 100}%` }} />
              </div>
            </div>

            {/* Segmented Progress Bars */}
            <div className="space-y-4 pt-2">
              <h4 className="font-bold text-xs text-gray-400 uppercase tracking-wider">Multi-Source Verification Metrics</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {confidenceBreakdown.map(item => (
                  <div key={item.label} className="p-3 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg space-y-2">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-gray-600 dark:text-gray-400">{item.label}</span>
                      <span className="text-gray-800 dark:text-gray-200">{item.value}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                      <div className={`h-full ${item.color} rounded-full`} style={{ width: `${item.value}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Business Impact Comparison */}
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm space-y-4">
            <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-500" /> Business Option Matrix Comparison
            </h3>
            <p className="text-xs text-gray-500">Compare top recommended actions against alternate playbooks orchestrated by the graph.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alternatives.map((alt, idx) => (
                <div 
                  key={idx} 
                  className={`p-4 rounded-xl border flex flex-col justify-between h-full transition ${
                    idx === 0 
                      ? 'border-blue-500 bg-blue-50/10 dark:bg-blue-950/10 ring-2 ring-blue-500/20' 
                      : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-sm text-gray-900 dark:text-gray-100 line-clamp-2">{alt.title}</h4>
                      {idx === 0 && <span className="text-[9px] uppercase font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200">WINNER</span>}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[10px] text-gray-500">
                      <div>ROI: <b className="text-emerald-500">${alt.roi.toLocaleString()}</b></div>
                      <div>Success: <b className="text-gray-700 dark:text-gray-300">{alt.successRate}%</b></div>
                      <div>Risk: <b className={alt.risk === 'High' ? 'text-red-500' : 'text-green-500'}>{alt.risk}</b></div>
                      <div>Timeline: <b>{alt.timeline}</b></div>
                    </div>

                    <div className="text-xs space-y-1.5 pt-2 border-t border-gray-100 dark:border-gray-800">
                      <p className="text-gray-600 dark:text-gray-400"><b>Pros:</b> {alt.pros}</p>
                      <p className="text-gray-600 dark:text-gray-400"><b>Cons:</b> {alt.cons}</p>
                    </div>
                  </div>

                  <div className="pt-3 mt-3 border-t border-gray-100 dark:border-gray-800 text-[10px] text-gray-500 italic">
                    {alt.reasoning}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Expandable Evidence Tabs & Context Sidebar */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4 shadow-sm">
            <h4 className="font-bold text-sm text-gray-900 dark:text-gray-100 mb-3">AI Explainability Trace</h4>
            <div className="space-y-2">
              {[
                { id: 'reasoning', title: 'Planner Reasoning Chain', icon: Brain, content: reasoningChain },
                { id: 'rules', title: 'Fired Business Rules', icon: Shield, content: triggeredRules },
              ].map(sec => {
                const isOpened = expandedSection === sec.id;
                const Icon = sec.icon;
                return (
                  <div key={sec.id} className="border border-gray-150 dark:border-gray-800 rounded-lg overflow-hidden">
                    <button 
                      onClick={() => toggleSection(sec.id)} 
                      className="w-full p-3 bg-gray-50 dark:bg-gray-800/40 flex items-center justify-between text-xs font-semibold text-gray-755 hover:bg-gray-100/50 transition-colors"
                    >
                      <span className="flex items-center gap-2"><Icon className="h-4 w-4 text-blue-500" /> {sec.title}</span>
                      {isOpened ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
                    </button>
                    {isOpened && (
                      <div className="p-3 bg-white dark:bg-gray-900 space-y-3 text-[11px] border-t border-gray-100 dark:border-gray-800 max-h-64 overflow-y-auto">
                        {sec.id === 'reasoning' && (sec.content as typeof reasoningChain).map((step, sIdx) => (
                          <div key={sIdx} className="space-y-0.5 border-b border-gray-100 dark:border-gray-850 pb-2 last:border-0 last:pb-0">
                            <span className="font-bold text-gray-800 dark:text-gray-200">{step.agent}</span>
                            <p className="text-gray-500">{step.action}</p>
                          </div>
                        ))}
                        {sec.id === 'rules' && (sec.content as typeof triggeredRules).map((rule, rIdx) => (
                          <div key={rIdx} className="space-y-0.5 border-b border-gray-100 dark:border-gray-850 pb-2 last:border-0 last:pb-0">
                            <span className="font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1">
                              <CheckCircle className="h-3.5 w-3.5 text-blue-500" /> {rule.title}
                            </span>
                            <p className="text-gray-500">{rule.desc}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {[
            { icon: FileText, title: 'Knowledge Sources', content: 'Index hits: premium_pricing_plan.pdf (Match Score: 98%), sales_playbook_v2.docx (Match Score: 85%)' },
            { icon: Calendar, title: 'Meeting Transcript Evidence', content: `"${rec.evidence || 'ssl timeline objections raised in contract terms discussion'}"` },
            { icon: Mail, title: 'Email Timeline Influence', content: 'Recent communications indicate SSO questions from developer staff.' },
            { icon: Brain, title: 'Historical Account Memory', content: 'Learned profile tags: High ARR client, prefers Slack updates, executive contact present.' },
          ].map((ctx, idx) => (
            <div key={idx} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4 shadow-sm hover:shadow-md transition">
              <div className="flex items-center gap-2 mb-2">
                <ctx.icon className="h-4 w-4 text-blue-500" />
                <h4 className="font-semibold text-sm text-gray-800 dark:text-gray-200">{ctx.title}</h4>
              </div>
              <p className="text-xs text-gray-650 dark:text-gray-400 leading-relaxed">{ctx.content}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
