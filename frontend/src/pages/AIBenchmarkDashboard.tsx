import React, { useState } from 'react';
import { 
  Activity, 
  ShieldCheck, 
  Gauge, 
  Layers, 
  CheckCircle, 
  Download, 
  Printer, 
  ArrowDownRight
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  LineChart,
  Line
} from 'recharts';

interface AgentMetric {
  name: string;
  executionTime: string;
  confidence: string;
  status: 'Healthy' | 'Warning' | 'Critical';
  successRate: string;
  tokens: string;
  cost: string;
  lastExecution: string;
}

export const AIBenchmarkDashboard: React.FC = () => {
  const [exporting, setExporting] = useState(false);

  // Agent Benchmark metrics
  const agentMetrics: AgentMetric[] = [
    { name: "Planner", executionTime: "0.12s", confidence: "100%", status: "Healthy", successRate: "100%", tokens: "320", cost: "$0.0004", lastExecution: "2s ago" },
    { name: "CRM", executionTime: "0.45s", confidence: "95%", status: "Healthy", successRate: "99.2%", tokens: "480", cost: "$0.0006", lastExecution: "2s ago" },
    { name: "Knowledge", executionTime: "0.78s", confidence: "88%", status: "Healthy", successRate: "97.5%", tokens: "1,200", cost: "$0.0018", lastExecution: "2s ago" },
    { name: "Memory", executionTime: "0.32s", confidence: "94%", status: "Healthy", successRate: "100%", tokens: "350", cost: "$0.0005", lastExecution: "3s ago" },
    { name: "Risk", executionTime: "1.12s", confidence: "90%", status: "Healthy", successRate: "98.1%", tokens: "850", cost: "$0.0012", lastExecution: "3s ago" },
    { name: "Opportunity", executionTime: "0.95s", confidence: "92%", status: "Healthy", successRate: "98.9%", tokens: "750", cost: "$0.0011", lastExecution: "3s ago" },
    { name: "Recommendation", executionTime: "1.45s", confidence: "94%", status: "Healthy", successRate: "99.4%", tokens: "1,540", cost: "$0.0023", lastExecution: "4s ago" },
    { name: "Human Review", executionTime: "0.08s", confidence: "100%", status: "Healthy", successRate: "100%", tokens: "120", cost: "$0.0001", lastExecution: "4s ago" }
  ];

  // Recharts Chart datasets
  const executionTimeData = [
    { name: 'Planner', Time: 0.12 },
    { name: 'CRM', Time: 0.45 },
    { name: 'Knowledge', Time: 0.78 },
    { name: 'Memory', Time: 0.32 },
    { name: 'Risk', Time: 1.12 },
    { name: 'Opportunity', Time: 0.95 },
    { name: 'Recommendation', Time: 1.45 }
  ];

  const confidenceData = [
    { name: 'Planner', Confidence: 100 },
    { name: 'CRM', Confidence: 95 },
    { name: 'Knowledge', Confidence: 88 },
    { name: 'Memory', Confidence: 94 },
    { name: 'Risk', Confidence: 90 },
    { name: 'Opportunity', Confidence: 92 },
    { name: 'Recommendation', Confidence: 94 }
  ];

  const successRateData = [
    { name: 'Planner', Rate: 100 },
    { name: 'CRM', Rate: 99.2 },
    { name: 'Knowledge', Rate: 97.5 },
    { name: 'Memory', Rate: 100 },
    { name: 'Risk', Rate: 98.1 },
    { name: 'Opportunity', Rate: 98.9 },
    { name: 'Recommendation', Rate: 99.4 }
  ];

  const reviewDistribution = [
    { name: 'Approved', value: 74, color: '#10B981' },
    { name: 'Rejected', value: 8, color: '#EF4444' },
    { name: 'Modified', value: 12, color: '#F59E0B' },
    { name: 'Pending', value: 6, color: '#3B82F6' }
  ];

  const costHistoryData = [
    { day: 'Mon', Cost: 0.85 },
    { day: 'Tue', Cost: 1.12 },
    { day: 'Wed', Cost: 0.94 },
    { day: 'Thu', Cost: 1.45 },
    { day: 'Fri', Cost: 1.21 },
    { day: 'Sat', Cost: 0.65 },
    { day: 'Sun', Cost: 0.88 }
  ];

  const topDocuments = [
    { name: "PricingPolicy.pdf", score: 0.94 },
    { name: "RenewalPlaybook.pdf", score: 0.91 },
    { name: "DiscountRules.pdf", score: 0.88 }
  ];

  const handleExport = (type: string) => {
    setExporting(true);
    setTimeout(() => {
      setExporting(false);
      alert(`${type} benchmark export completed successfully.`);
    }, 1500);
  };

  return (
    <div className="space-y-8 p-6 pb-12 bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-200 dark:border-gray-800 pb-5">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-500 bg-clip-text text-transparent">
            AI Observability & Benchmark Dashboard
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Real-time multi-agent health status, model evaluation latency, token metrics, and caching performance.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => handleExport("PDF")}
            disabled={exporting}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg text-xs font-semibold shadow hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2 transition-all"
          >
            <Download className="h-4 w-4" />
            <span>{exporting ? "Generating..." : "Export PDF"}</span>
          </button>
          <button 
            onClick={() => handleExport("CSV")}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-lg text-xs font-semibold shadow hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2 transition-all"
          >
            <Layers className="h-4 w-4" />
            <span>Export CSV</span>
          </button>
          <button 
            onClick={() => window.print()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow flex items-center space-x-2 transition-all"
          >
            <Printer className="h-4 w-4" />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Top Ring Gauges: AI Health Score & Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm flex items-center justify-between">
          <div className="space-y-2">
            <span className="text-xs text-gray-500 font-bold uppercase tracking-wider block">AI Observability Health</span>
            <h3 className="text-3xl font-extrabold text-gray-950 dark:text-white">96 / 100</h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300">
              Healthy
            </span>
            <p className="text-xs text-gray-400 mt-2">Aggregate index of average confidence match, success counts, latency thresholds, and API error rates.</p>
          </div>
          <div className="relative h-28 w-28 flex items-center justify-center">
            <svg className="absolute transform -rotate-90 w-24 h-24">
              <circle cx="48" cy="48" r="40" stroke="currentColor" className="text-gray-100 dark:text-gray-800" strokeWidth="8" fill="transparent" />
              <circle cx="48" cy="48" r="40" stroke="currentColor" className="text-green-500" strokeWidth="8" fill="transparent" strokeDasharray="251" strokeDashoffset="10" />
            </svg>
            <Gauge className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="p-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm flex items-center justify-between">
          <div className="space-y-2">
            <span className="text-xs text-gray-500 font-bold uppercase tracking-wider block">AI Quality Index</span>
            <h3 className="text-3xl font-extrabold text-gray-950 dark:text-white">97 / 100</h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              Excellent
            </span>
            <p className="text-xs text-gray-400 mt-2">Evaluates response precision schema formats, RAG chunk retrieval counts, and manager approval ratios.</p>
          </div>
          <div className="relative h-28 w-28 flex items-center justify-center">
            <svg className="absolute transform -rotate-90 w-24 h-24">
              <circle cx="48" cy="48" r="40" stroke="currentColor" className="text-gray-100 dark:text-gray-800" strokeWidth="8" fill="transparent" />
              <circle cx="48" cy="48" r="40" stroke="currentColor" className="text-blue-500" strokeWidth="8" fill="transparent" strokeDasharray="251" strokeDashoffset="7" />
            </svg>
            <Activity className="h-8 w-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Model Overview grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Model Engine</span>
          <p className="font-extrabold text-lg text-blue-600 dark:text-blue-400">Gemini 2.5 Pro</p>
          <span className="text-[10px] text-gray-400">Provider: Gemini SDK</span>
        </div>
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Avg Response Latency</span>
          <p className="font-extrabold text-lg text-amber-500">1.21 sec</p>
          <span className="text-[10px] text-green-500 flex items-center">
            <ArrowDownRight className="h-3 w-3 mr-0.5" /> 8% vs yesterday
          </span>
        </div>
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Total API Calls Today</span>
          <p className="font-extrabold text-lg">325</p>
          <span className="text-[10px] text-gray-400">319 Success / 6 Failed</span>
        </div>
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Fallback & Retry Rates</span>
          <p className="font-extrabold text-lg">2%</p>
          <span className="text-[10px] text-gray-400">14 retries registered</span>
        </div>
      </div>

      {/* Agent Performance table */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">LangGraph Agent Benchmarks</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                <th className="pb-3 font-semibold">Agent Node</th>
                <th className="pb-3 font-semibold text-center">Execution Time</th>
                <th className="pb-3 font-semibold text-center">Avg Confidence</th>
                <th className="pb-3 font-semibold text-center">Status</th>
                <th className="pb-3 font-semibold text-center">Success Rate</th>
                <th className="pb-3 font-semibold text-center">Avg Tokens</th>
                <th className="pb-3 font-semibold text-center">Avg Cost</th>
                <th className="pb-3 font-semibold text-right">Last Running</th>
              </tr>
            </thead>
            <tbody>
              {agentMetrics.map((agent, i) => (
                <tr key={i} className="border-b border-gray-100 dark:border-gray-850 hover:bg-gray-50 dark:hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 font-bold text-gray-900 dark:text-gray-200">{agent.name} Agent</td>
                  <td className="py-3 text-center">{agent.executionTime}</td>
                  <td className="py-3 text-center text-blue-500 font-bold">{agent.confidence}</td>
                  <td className="py-3 text-center">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                      {agent.status}
                    </span>
                  </td>
                  <td className="py-3 text-center font-semibold text-emerald-500">{agent.successRate}</td>
                  <td className="py-3 text-center text-gray-500">{agent.tokens}</td>
                  <td className="py-3 text-center font-medium text-emerald-600">{agent.cost}</td>
                  <td className="py-3 text-right text-gray-400">{agent.lastExecution}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Agent Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="font-bold text-sm">Average Execution Time (Seconds)</h4>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={executionTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                <XAxis dataKey="name" stroke="#6B7280" fontSize={9} />
                <YAxis stroke="#6B7280" fontSize={9} />
                <Tooltip />
                <Bar dataKey="Time" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="font-bold text-sm">Confidence Metrics (%)</h4>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                <XAxis dataKey="name" stroke="#6B7280" fontSize={9} />
                <YAxis stroke="#6B7280" fontSize={9} />
                <Tooltip />
                <Bar dataKey="Confidence" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="font-bold text-sm">Agent Success Distribution (%)</h4>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={successRateData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                <XAxis dataKey="name" stroke="#6B7280" fontSize={9} />
                <YAxis stroke="#6B7280" fontSize={9} />
                <Tooltip />
                <Bar dataKey="Rate" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* LLM Usage section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Prompt Tokens</span>
          <p className="font-extrabold text-lg text-blue-600 dark:text-blue-400 font-bold">2,345</p>
          <span className="text-[10px] text-gray-400 font-semibold block">Source: Gemini Observability</span>
        </div>
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Completion Tokens</span>
          <p className="font-extrabold text-lg text-emerald-500">564</p>
          <span className="text-[10px] text-gray-400 font-semibold block">Source: Gemini Observability</span>
        </div>
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Total Token Vol</span>
          <p className="font-extrabold text-lg">2,909</p>
          <span className="text-[10px] text-gray-400">Avg token size: 720</span>
        </div>
        <div className="p-5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm space-y-1">
          <span className="text-xs text-gray-500 font-medium">Monthly Cost Projection</span>
          <p className="font-extrabold text-lg text-emerald-600">$124.50</p>
          <span className="text-[10px] text-gray-400">Based on $0.0041/call avg</span>
        </div>
      </div>

      {/* RAG Benchmark + Explainability Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Hybrid RAG Performance</h3>
          
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-150 dark:border-gray-800">
              <span className="text-[10px] text-gray-500 block">Indexed Docs</span>
              <span className="font-bold text-base text-blue-600 dark:text-blue-400">24</span>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-150 dark:border-gray-800">
              <span className="text-[10px] text-gray-500 block">Avg Retrieval</span>
              <span className="font-bold text-base text-amber-500">0.18s</span>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-150 dark:border-gray-800">
              <span className="text-[10px] text-gray-500 block">Similarity Score</span>
              <span className="font-bold text-base text-emerald-500">0.91</span>
            </div>
          </div>

          <div className="space-y-3">
            <span className="font-bold text-xs text-gray-700 dark:text-gray-300 block">Top Searched Playbooks</span>
            {topDocuments.map((doc, idx) => (
              <div key={idx} className="space-y-1 text-xs">
                <div className="flex justify-between font-semibold">
                  <span>{doc.name}</span>
                  <span className="text-blue-500">score {doc.score}</span>
                </div>
                <div className="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full" style={{ width: `${doc.score * 100}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Explainability & Citations</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-gray-500 block text-xs">Total Recommendations</span>
              <p className="font-extrabold text-2xl text-blue-600 mt-1">428</p>
            </div>
            <div className="p-4 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-gray-500 block text-xs">Approved by Managers</span>
              <p className="font-extrabold text-2xl text-emerald-500 mt-1">396</p>
            </div>
            <div className="p-4 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-gray-500 block text-xs">Rejected or Modified</span>
              <p className="font-extrabold text-2xl text-amber-500 mt-1">32</p>
            </div>
            <div className="p-4 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-gray-500 block text-xs">Avg Source Citations</span>
              <p className="font-extrabold text-2xl mt-1">3.4 docs</p>
            </div>
          </div>
        </div>
      </div>

      {/* Human Review Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Manager Action Distribution</h3>
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="h-44 w-44">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={reviewDistribution}
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {reviewDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-2 text-xs">
              {reviewDistribution.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                    <span className="font-medium">{item.name}</span>
                  </div>
                  <span className="font-bold">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Review Latency & Audits</h3>
          <div className="space-y-4 text-xs">
            <div className="flex justify-between border-b border-gray-100 dark:border-gray-800 pb-2">
              <span className="text-gray-500">Average review duration</span>
              <span className="font-bold text-gray-850 dark:text-gray-200">12.4 seconds</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 dark:border-gray-800 pb-2">
              <span className="text-gray-500">Acceptance threshold score</span>
              <span className="font-bold text-green-500">92.5%</span>
            </div>
            <div className="flex justify-between pb-2">
              <span className="text-gray-500">Self-Rejection / Escalation rate</span>
              <span className="font-bold text-rose-500">1.8%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Redis cache & security metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Redis Performance Cache</h3>
            <span className="text-[10px] text-gray-500 font-bold bg-amber-500/10 px-2 py-0.5 rounded text-amber-500">Demo Mode</span>
          </div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-[10px] text-gray-500 block">Cache hit ratio</span>
              <span className="font-bold text-lg text-blue-600 dark:text-blue-400">84.2%</span>
            </div>
            <div className="p-3 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-[10px] text-gray-500 block">Active keys</span>
              <span className="font-bold text-lg">128</span>
            </div>
            <div className="p-3 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-[10px] text-gray-500 block">Invalidations today</span>
              <span className="font-bold text-lg text-emerald-500">42</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Security Metrics</h3>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-150 dark:border-gray-800 flex items-center justify-between">
              <div>
                <span className="text-gray-500 block text-[10px]">Prompt Injections Blocked</span>
                <span className="font-extrabold text-base text-rose-500 mt-1">12</span>
              </div>
              <ShieldCheck className="h-5 w-5 text-rose-500" />
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-150 dark:border-gray-800 flex items-center justify-between">
              <div>
                <span className="text-gray-500 block text-[10px]">TOTP MFA Enabled Users</span>
                <span className="font-extrabold text-base text-green-500 mt-1">100%</span>
              </div>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
          </div>
        </div>
      </div>

      {/* SSE & Cost History Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">SSE Streaming Events</h3>
            <div className="flex items-center space-x-2">
              <span className="h-2.5 w-2.5 rounded-full bg-green-500 animate-ping"></span>
              <span className="text-[10px] text-green-500 font-bold uppercase">Streaming live</span>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-[10px] text-gray-500 block">Total events today</span>
              <span className="font-bold text-lg text-blue-600 dark:text-blue-400">1,248</span>
            </div>
            <div className="p-3 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-[10px] text-gray-500 block">Average stream delay</span>
              <span className="font-bold text-lg">0.05s</span>
            </div>
            <div className="p-3 border border-gray-150 dark:border-gray-800 rounded-xl">
              <span className="text-[10px] text-gray-500 block">Dropped sessions</span>
              <span className="font-bold text-lg text-green-500">0</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">AI Cost Stream History</h3>
            <span className="text-[10px] text-gray-500 font-bold bg-amber-500/10 px-2 py-0.5 rounded text-amber-500">Estimated Cost</span>
          </div>
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={costHistoryData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="day" stroke="#6B7280" fontSize={9} />
                <YAxis stroke="#6B7280" fontSize={9} />
                <Tooltip />
                <Line type="monotone" dataKey="Cost" stroke="#10B981" strokeWidth={2.5} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* System Health Section */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Active System Health status</h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-center">
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-xs font-bold">
            Gemini SDK: Healthy
          </div>
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-xs font-bold">
            FastAPI: Healthy
          </div>
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-xs font-bold">
            SQLite: Healthy
          </div>
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-xs font-bold">
            Redis: Healthy
          </div>
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-xs font-bold">
            ChromaDB: Healthy
          </div>
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-xs font-bold">
            SSE Node: Running
          </div>
        </div>
      </div>

      {/* Live Activity Feed */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-extrabold text-lg text-gray-950 dark:text-white">Live Benchmark Event Stream</h3>
        <div className="space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-100 dark:before:bg-gray-800 text-xs">
          <div className="relative pl-8">
            <span className="absolute left-1.5 top-1.5 h-3.5 w-3.5 rounded-full bg-blue-500 border-2 border-white dark:border-gray-900 flex items-center justify-center"></span>
            <div className="space-y-1">
              <span className="text-gray-400 text-[10px] block">12:15:02</span>
              <p className="font-semibold">Planner Node Compiled Active execution itinerary</p>
            </div>
          </div>
          <div className="relative pl-8">
            <span className="absolute left-1.5 top-1.5 h-3.5 w-3.5 rounded-full bg-purple-500 border-2 border-white dark:border-gray-900 flex items-center justify-center"></span>
            <div className="space-y-1">
              <span className="text-gray-400 text-[10px] block">12:15:05</span>
              <p className="font-semibold">Knowledge Node Index matched 7 document playbooks</p>
            </div>
          </div>
          <div className="relative pl-8">
            <span className="absolute left-1.5 top-1.5 h-3.5 w-3.5 rounded-full bg-amber-500 border-2 border-white dark:border-gray-900 flex items-center justify-center"></span>
            <div className="space-y-1">
              <span className="text-gray-400 text-[10px] block">12:15:10</span>
              <p className="font-semibold">Gemini SDK response compiled in 1.21s (Success)</p>
            </div>
          </div>
          <div className="relative pl-8">
            <span className="absolute left-1.5 top-1.5 h-3.5 w-3.5 rounded-full bg-green-500 border-2 border-white dark:border-gray-900 flex items-center justify-center"></span>
            <div className="space-y-1">
              <span className="text-gray-400 text-[10px] block">12:16:15</span>
              <p className="font-semibold">Manager approved recommendation card #28</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
