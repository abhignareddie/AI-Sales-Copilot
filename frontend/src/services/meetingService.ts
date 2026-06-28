import { apiDelete, apiGet, apiPost, apiPut } from '../lib/api';
import { MOCK_MEETINGS } from '../lib/mockData';
import type { Meeting } from '../types';

export const meetingService = {
  async list(): Promise<Meeting[]> {
    try {
      const data = await apiGet<Meeting[] | { items: Meeting[] }>('/meetings');
      return Array.isArray(data) ? data : data.items || [];
    } catch {
      return MOCK_MEETINGS;
    }
  },

  async get(id: number): Promise<Meeting> {
    try {
      return await apiGet<Meeting>(`/meetings/${id}`);
    } catch {
      const found = MOCK_MEETINGS.find(m => m.id === id);
      if (!found) throw new Error('Meeting not found');
      return found;
    }
  },

  async create(data: Omit<Meeting, 'id'>): Promise<Meeting> {
    try {
      const created = await apiPost<Meeting>('/meetings', data);
      try {
        await apiPost('/recommendations/generate', { customer_id: data.customer_id });
      } catch {
        // optional trigger
      }
      return created;
    } catch {
      return { id: Date.now(), ...data };
    }
  },

  async update(id: number, data: Partial<Meeting>): Promise<Meeting> {
    try {
      return await apiPut<Meeting>(`/meetings/${id}`, data);
    } catch {
      const existing = MOCK_MEETINGS.find(m => m.id === id) || MOCK_MEETINGS[0];
      return { ...existing, ...data };
    }
  },

  async remove(id: number): Promise<void> {
    try {
      await apiDelete(`/meetings/${id}`);
    } catch {
      // demo fallback
    }
  },
};
