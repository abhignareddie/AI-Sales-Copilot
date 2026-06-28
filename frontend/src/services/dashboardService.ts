import { apiGet } from '../lib/api';
import { DEFAULT_DASHBOARD_STATS } from '../lib/mockData';
import type { DashboardStats } from '../types';

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    try {
      const data = await apiGet<DashboardStats>('/dashboard/stats');
      const avgHealth = data.health_score_distribution
        ? Object.entries(data.health_score_distribution).reduce((sum, [, v]) => sum + v, 0) /
          Math.max(Object.keys(data.health_score_distribution).length, 1)
        : 62.5;
      return {
        ...DEFAULT_DASHBOARD_STATS,
        ...data,
        total_emails: data.total_emails ?? 24,
        accepted_recommendations: data.completed_recommendations ?? data.accepted_recommendations ?? 0,
        open_risks: data.open_tickets ?? data.open_risks ?? 0,
        projected_revenue: `$${((data.total_revenue || 0) * 0.08).toLocaleString(undefined, { maximumFractionDigits: 0 })}`,
        total_pipeline: `$${((data.total_revenue || 0) * 0.9 / 1000).toFixed(1)}M`,
        pending_actions: data.pending_recommendations,
        avg_health: `${avgHealth.toFixed(1)}%`,
      };
    } catch {
      return DEFAULT_DASHBOARD_STATS;
    }
  },
};
