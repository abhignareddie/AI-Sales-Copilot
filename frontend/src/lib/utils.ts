import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO } from 'date-fns';

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));

export const getPriorityStyle = (prio: string) => {
  const styles: Record<string, string> = {
    high: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800',
    medium: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800',
    low: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
  };
  const key = prio?.toLowerCase() || 'medium';
  return `inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${styles[key] || 'bg-gray-50 text-gray-700 border-gray-200'}`;
};

export const getStatusStyle = (status: string) => {
  const normalized = status?.toLowerCase() || '';
  const map: Record<string, string> = {
    'pending review': 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800',
    pending: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800',
    approved: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
    implemented: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
    rejected: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-800',
    open: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800',
    closed: 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700',
    sent: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800',
  };
  return `inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${map[normalized] || 'bg-gray-50 text-gray-700 border-gray-200'}`;
};

export const formatCurrency = (value?: number | null) => {
  if (value == null) return '—';
  return `$${value.toLocaleString()}`;
};

export const formatDate = (value?: string | null) => {
  if (!value) return '—';
  try {
    return format(parseISO(value), 'MMM d, yyyy');
  } catch {
    return value;
  }
};

export const formatRelative = (value?: string | null) => {
  if (!value) return '—';
  try {
    return formatDistanceToNow(parseISO(value), { addSuffix: true });
  } catch {
    return value;
  }
};

export const derivePriority = (confidence: number): string => {
  if (confidence >= 0.85) return 'high';
  if (confidence >= 0.65) return 'medium';
  return 'low';
};

export const normalizeRecommendation = (rec: Record<string, unknown>) => ({
  ...rec,
  priority: (rec.priority as string) || derivePriority((rec.confidence as number) || 0),
  title: (rec.title as string) || (rec.recommendation as string)?.slice(0, 80),
  status: normalizeStatus(rec.status as string),
  company: rec.company as string,
  roi: (rec.roi as number) || Math.round(((rec.confidence as number) || 0.7) * 20000),
  business_impact: (rec.business_impact as string) || 'Revenue retention & pipeline acceleration',
  reasoning: (rec.reasoning as string) || (rec.evidence as string) || 'Multi-agent analysis synthesized customer signals.',
  suggested_action: (rec.suggested_action as string) || (rec.recommendation as string),
});

export const normalizeStatus = (status: string) => {
  const map: Record<string, string> = {
    pending: 'Pending Review',
    approved: 'Approved',
    rejected: 'Rejected',
    implemented: 'Approved',
  };
  return map[status?.toLowerCase()] || status || 'Pending Review';
};
