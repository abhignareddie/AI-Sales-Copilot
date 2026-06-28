import { useState } from 'react';
import { 
  CheckCircle, Play, AlertCircle, Clock, Database, Brain, Users, Calendar, FileText, Sparkles, ChevronDown, ChevronUp
} from 'lucide-react';
import type { AgentStep } from '../../types';

interface AgentNodeProps {
  step: AgentStep & {
    whySelected?: string;
    inputReceived?: string;
    documentsUsed?: string;
    memoryUsedCount?: number;
    reasoningSteps?: string[];
  };
  index: number;
  isLast?: boolean;
  isActive?: boolean;
  isComplete?: boolean;
  isFailed?: boolean;
}

export const AgentNode = ({ step, isLast, isActive, isComplete, isFailed }: AgentNodeProps) => {
  const [expanded, setExpanded] = useState(false);

  const getAgentIcon = (name: string) => {
    switch (name) {
      case 'Planner Agent': return <Brain className="h-5 w-5 text-blue-500" />;
      case 'Meeting Agent': return <Calendar className="h-5 w-5 text-purple-500" />;
      case 'CRM Agent': return <Users className="h-5 w-5 text-emerald-500" />;
      case 'Knowledge Agent': return <FileText className="h-5 w-5 text-amber-500" />;
      case 'Memory Agent': return <Database className="h-5 w-5 text-cyan-500" />;
      case 'Risk Agent': return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'Recommendation Agent': return <Sparkles className="h-5 w-5 text-violet-500" />;
      default: return <ActivityIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = () => {
    if (isActive) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold text-blue-600 bg-blue-50 dark:bg-blue-950/30 rounded-full border border-blue-200 dark:border-blue-900/30 animate-pulse">
          <Play className="h-3 w-3 animate-spin" /> RUNNING
        </span>
      );
    }
    if (isComplete) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold text-green-600 bg-green-50 dark:bg-green-950/30 rounded-full border border-green-200 dark:border-green-900/30">
          <CheckCircle className="h-3 w-3" /> COMPLETE
        </span>
      );
    }
    if (isFailed) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold text-red-600 bg-red-50 dark:bg-red-950/30 rounded-full border border-red-200 dark:border-red-900/30">
          <AlertCircle className="h-3 w-3" /> FAILED
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold text-gray-500 bg-gray-50 dark:bg-gray-800 rounded-full border border-gray-200 dark:border-gray-700">
        <Clock className="h-3 w-3" /> IDLE
      </span>
    );
  };

  return (
    <div className="flex flex-col items-center w-full max-w-2xl mx-auto">
      <div
        className={`w-full border rounded-xl transition-all duration-300 overflow-hidden shadow-sm hover:shadow-md ${
          isActive
            ? 'border-blue-500 bg-blue-50/20 dark:bg-blue-950/10 ring-2 ring-blue-500/20 scale-[1.01]'
            : isComplete
              ? 'border-green-200 dark:border-green-900/30 bg-green-50/10 dark:bg-green-950/5'
              : isFailed
                ? 'border-red-200 dark:border-red-900/30 bg-red-50/10 dark:bg-red-950/5'
                : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900'
        }`}
      >
        {/* Node Summary Bar */}
        <div 
          onClick={() => setExpanded(!expanded)} 
          className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
              {getAgentIcon(step.name)}
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-900 dark:text-gray-100">{step.name}</h4>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{step.desc}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {getStatusBadge()}
            {expanded ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
          </div>
        </div>

        {/* Collapsible Node Details Panel */}
        {expanded && (
          <div className="p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-950/20 space-y-4 text-xs">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-gray-500">
              <div className="p-2.5 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="block text-[10px] uppercase font-semibold text-gray-400">Duration</span>
                <span className="text-sm font-bold text-gray-800 dark:text-gray-200 mt-1 block">{step.duration}</span>
              </div>
              <div className="p-2.5 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="block text-[10px] uppercase font-semibold text-gray-400">Tokens</span>
                <span className="text-sm font-bold text-gray-800 dark:text-gray-200 mt-1 block">{step.tokens.toLocaleString()}</span>
              </div>
              <div className="p-2.5 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="block text-[10px] uppercase font-semibold text-gray-400">Confidence</span>
                <span className="text-sm font-bold text-blue-600 dark:text-blue-400 mt-1 block">{step.confidence}</span>
              </div>
              <div className="p-2.5 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="block text-[10px] uppercase font-semibold text-gray-400">Memory Allocation</span>
                <span className="text-sm font-bold text-gray-800 dark:text-gray-200 mt-1 block">{step.memory}</span>
              </div>
            </div>

            {step.whySelected && (
              <div className="p-3 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="font-bold text-gray-700 dark:text-gray-300 block mb-1">Reason Selected</span>
                <p className="text-gray-600 dark:text-gray-400">{step.whySelected}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="font-bold text-gray-700 dark:text-gray-300 block mb-1">Input Context</span>
                <p className="text-gray-650 dark:text-gray-450 italic font-mono text-[11px]">{step.inputReceived || 'System state parameters loaded'}</p>
              </div>
              <div className="p-3 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="font-bold text-gray-700 dark:text-gray-300 block mb-1">Output Summary</span>
                <p className="text-gray-650 dark:text-gray-450 font-mono text-[11px]">{step.resultSummary || 'Awaiting execution'}</p>
              </div>
            </div>

            {step.reasoningSteps && step.reasoningSteps.length > 0 && (
              <div className="p-3 bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-850 rounded-lg">
                <span className="font-bold text-gray-700 dark:text-gray-300 block mb-2">Internal Agent Reasoning Steps</span>
                <ul className="space-y-1.5 list-disc pl-4 text-gray-600 dark:text-gray-400">
                  {step.reasoningSteps.map((rs, idx) => <li key={idx}>{rs}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Connection Edge */}
      {!isLast && (
        <div className="flex flex-col items-center py-2 h-10">
          <div className={`w-0.5 h-full transition-all duration-300 ${
            isActive || isComplete 
              ? 'bg-gradient-to-b from-blue-500 to-indigo-500 shadow shadow-indigo-500/50' 
              : 'bg-gray-200 dark:bg-gray-800'
          }`} />
        </div>
      )}
    </div>
  );
};

const ActivityIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

export const AGENT_PIPELINE: (AgentStep & {
  whySelected?: string;
  inputReceived?: string;
  documentsUsed?: string;
  memoryUsedCount?: number;
  reasoningSteps?: string[];
})[] = [
  { 
    name: 'Planner Agent', 
    desc: 'Formulates optimal multi-agent itinerary.', 
    duration: '0.1s', 
    confidence: '100%', 
    tokens: 420, 
    docs: 0, 
    memory: '0.5MB', 
    retries: 0, 
    status: 'idle', 
    resultSummary: 'Orchestration plan compiled for 6 downstream agents',
    whySelected: 'Always active as the initial state node to parse and structure context.',
    inputReceived: 'Customer telemetry variables: Health Score, Stage, Industry, ARR, open tickets count.',
    reasoningSteps: [
      'Parsed incoming customer payload containing metrics.',
      'Identified critical health score drop (under 50 threshold).',
      'Routed downstream nodes to trigger Risk and Support audit agents in parallel.'
    ]
  },
  { 
    name: 'Meeting Agent', 
    desc: 'Analyzes transcripts and meeting summaries.', 
    duration: '0.5s', 
    confidence: '93%', 
    tokens: 1240, 
    docs: 0, 
    memory: '1.0MB', 
    retries: 0, 
    status: 'idle', 
    resultSummary: 'Extracted 4 action items from latest meeting',
    whySelected: 'Selected dynamically because customer records contain unreviewed meeting transcripts.',
    inputReceived: 'Raw Q2 transcript lines with Acme Corporation stakeholders.',
    reasoningSteps: [
      'Tokenized meeting conversation text.',
      'Recognized mentions of pricing objections and competitors.',
      'Extracted core concerns: SSO integration delay and timeline risks.'
    ]
  },
  { 
    name: 'CRM Agent', 
    desc: 'Extracts profiles & historical deal values.', 
    duration: '0.4s', 
    confidence: '95%', 
    tokens: 890, 
    docs: 0, 
    memory: '1.2MB', 
    retries: 0, 
    status: 'idle', 
    resultSummary: 'Retrieved customer profile and $150K ARR deal',
    whySelected: 'Required to anchor financial forecasts and deal stage classifications.',
    inputReceived: 'Acme Corporation CRM customer id.',
    reasoningSteps: [
      'Queried customers table for annual revenue and sizing metrics.',
      'Found ARR matches $150K with open renewal date within 30 days.'
    ]
  },
  { 
    name: 'Knowledge Agent', 
    desc: 'Queries playbooks & pricing guides.', 
    duration: '0.8s', 
    confidence: '88%', 
    tokens: 2100, 
    docs: 4, 
    memory: '2.4MB', 
    retries: 0, 
    status: 'idle', 
    resultSummary: 'Matched 4 relevant playbook sections',
    whySelected: 'Fired to search playbooks when pricing concerns or timeline objections are found in meetings.',
    inputReceived: 'Search query: SSO timeline pricing negotiations.',
    reasoningSteps: [
      'Performed hybrid retrieval (Chroma + BM25) on playbooks.',
      'Extracted top match: premium_pricing_plan.pdf.',
      'Isolated sections detailing discount rules for SSO add-ons.'
    ]
  },
  { 
    name: 'Memory Agent', 
    desc: 'Retrieves historical interactions & preferences.', 
    duration: '0.6s', 
    confidence: '91%', 
    tokens: 760, 
    docs: 0, 
    memory: '3.1MB', 
    retries: 0, 
    status: 'idle', 
    resultSummary: 'Loaded 12 prior interactions and preferences',
    whySelected: 'Triggered to evaluate past account context and communications history.',
    inputReceived: 'Historical account ID.',
    reasoningSteps: [
      'Pulled memory timeline entries containing 12 logged interactions.',
      'Extracted preference key: Prefers updates via Slack channels; VP handles final approvals.'
    ]
  },
  { 
    name: 'Risk Agent', 
    desc: 'Computes retention and churn indicators.', 
    duration: '1.5s', 
    confidence: '90%', 
    tokens: 980, 
    docs: 0, 
    memory: '3.2MB', 
    retries: 1, 
    status: 'idle', 
    resultSummary: 'Medium churn risk — health score below threshold',
    whySelected: 'Invoked due to customer health score dropping below warning limits.',
    inputReceived: 'Health score: 48%',
    reasoningSteps: [
      'Compared health score (48%) against escalation playbook limits (50%).',
      'Flagged risk status as MEDIUM risk.'
    ]
  },
  { 
    name: 'Recommendation Agent', 
    desc: 'Assembles explainable next action lists.', 
    duration: '2.1s', 
    confidence: '94%', 
    tokens: 1850, 
    docs: 2, 
    memory: '4.0MB', 
    retries: 0, 
    status: 'idle', 
    resultSummary: 'Generated 3 prioritized next best actions',
    whySelected: 'Fires to synthesize outputs from Risk, Knowledge, and CRM agents into a concrete NBA recommendation.',
    inputReceived: 'Aggregated findings from Planner downstream graph nodes.',
    reasoningSteps: [
      'Combined pricing guides with timeline constraints.',
      'Drafted main NBA action: Schedule immediate VP proposal alignment review.'
    ]
  },
];
