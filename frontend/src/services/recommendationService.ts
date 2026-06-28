import { apiGet, apiPost } from '../lib/api';
import { MOCK_RECOMMENDATIONS } from '../lib/mockData';
import { normalizeRecommendation } from '../lib/utils';
import type { Recommendation } from '../types';

export const recommendationService = {
  async list(): Promise<Recommendation[]> {
    try {
      const data = await apiGet<Recommendation[] | { items: Recommendation[] }>('/recommendations');
      const items = Array.isArray(data) ? data : data.items || [];
      return items.map(r => normalizeRecommendation(r as unknown as Record<string, unknown>)) as Recommendation[];
    } catch {
      return MOCK_RECOMMENDATIONS;
    }
  },

  async get(id: number): Promise<Recommendation> {
    try {
      const rec = await apiGet<Recommendation>(`/recommendations/${id}`);
      return normalizeRecommendation(rec as unknown as Record<string, unknown>) as Recommendation;
    } catch {
      const found = MOCK_RECOMMENDATIONS.find(r => r.id === id);
      if (!found) throw new Error('Recommendation not found');
      return found;
    }
  },

  async getByCustomer(customerId: number): Promise<Recommendation[]> {
    try {
      const data = await apiGet<Recommendation[]>(`/recommendations/customer/${customerId}`);
      return data.map(r => normalizeRecommendation(r as unknown as Record<string, unknown>)) as Recommendation[];
    } catch {
      return MOCK_RECOMMENDATIONS.filter(r => r.customer_id === customerId);
    }
  },

  async approve(id: number, comments?: string): Promise<void> {
    try {
      await apiPost('/review/approve', { recommendation_id: id, comments });
    } catch {
      await apiPost('/recommendations/approve', { recommendation_id: id, comments }).catch(() => {});
    }
  },

  async reject(id: number, comments?: string): Promise<void> {
    try {
      await apiPost('/review/reject', { recommendation_id: id, comments });
    } catch {
      await apiPost('/recommendations/reject', { recommendation_id: id, comments }).catch(() => {});
    }
  },

  async generate(customerId: number): Promise<void> {
    try {
      await apiPost('/recommendations/generate', { customer_id: customerId });
    } catch {
      // demo fallback
    }
  },

  async addFeedback(id: number, feedback: string): Promise<void> {
    try {
      await apiPost('/review/comment', { recommendation_id: id, content: feedback });
    } catch {
      // demo fallback
    }
  },
};
