import { apiDelete, apiGet, apiPost, apiPut } from '../lib/api';
import { MOCK_EMAILS } from '../lib/mockData';
import type { Email } from '../types';

export const emailService = {
  async list(): Promise<Email[]> {
    try {
      const data = await apiGet<Email[] | { items: Email[] }>('/emails');
      return Array.isArray(data) ? data : data.items || [];
    } catch {
      return MOCK_EMAILS;
    }
  },

  async get(id: number): Promise<Email> {
    try {
      return await apiGet<Email>(`/emails/${id}`);
    } catch {
      const found = MOCK_EMAILS.find(e => e.id === id);
      if (!found) throw new Error('Email not found');
      return found;
    }
  },

  async create(data: Omit<Email, 'id'>): Promise<Email> {
    try {
      return await apiPost<Email>('/emails', {
        customer_id: data.customer_id,
        subject: data.subject,
        sender: data.sender,
        receiver: data.receiver,
        body: data.body,
      });
    } catch {
      return { id: Date.now(), ...data, status: data.status || 'sent' };
    }
  },

  async update(id: number, data: Partial<Email>): Promise<Email> {
    try {
      return await apiPut<Email>(`/emails/${id}`, data);
    } catch {
      const existing = MOCK_EMAILS.find(e => e.id === id) || MOCK_EMAILS[0];
      return { ...existing, ...data };
    }
  },

  async remove(id: number): Promise<void> {
    try {
      await apiDelete(`/emails/${id}`);
    } catch {
      // demo fallback
    }
  },
};
