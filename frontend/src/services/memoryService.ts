import { apiGet, apiPost } from '../lib/api';
import { MOCK_MEMORY } from '../lib/mockData';
import type { MemoryEntry, TimelineItem } from '../types';

export const memoryService = {
  async list(customerId?: number): Promise<MemoryEntry[]> {
    try {
      const data = await apiGet<MemoryEntry[] | { items: MemoryEntry[] }>('/memories');
      const items = Array.isArray(data) ? data : data.items || [];
      return customerId ? items.filter(m => m.customer_id === customerId) : items;
    } catch {
      return customerId ? MOCK_MEMORY.filter(m => m.customer_id === customerId) : MOCK_MEMORY;
    }
  },

  async getCustomerMemory(customerId: number): Promise<Record<string, unknown>> {
    try {
      return await apiGet<Record<string, unknown>>(`/memory/customer/${customerId}`);
    } catch {
      return {
        previous_meetings: MOCK_MEMORY.filter(m => m.memory_type === 'interaction'),
        past_recommendations: [],
        accepted_actions: [],
        rejected_actions: [],
      };
    }
  },

  async getTimeline(customerId: number): Promise<TimelineItem[]> {
    try {
      const data = await apiGet<{ items: TimelineItem[] } | TimelineItem[]>(`/timeline/customer/${customerId}`);
      return Array.isArray(data) ? data : data.items || [];
    } catch {
      return MOCK_MEMORY.filter(m => m.customer_id === customerId).map(m => ({
        id: m.id,
        timestamp: m.created_at,
        title: String(m.memory_data.title || m.memory_type),
        description: String(m.memory_data.note || ''),
        type: m.memory_type,
      }));
    }
  },

  async search(query: string, customerId?: number): Promise<MemoryEntry[]> {
    try {
      return await apiPost<MemoryEntry[]>('/memory/search', { query, customer_id: customerId });
    } catch {
      return MOCK_MEMORY;
    }
  },
};
